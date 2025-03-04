import logging
from datetime import datetime
from typing import Any, Dict, List
import json

import sqlalchemy
from sqlalchemy import Column, MetaData, Table, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql.sqltypes import NullType

from langchain_core.prompts import ChatPromptTemplate

from app.api.requests import ScannerRequest
from app.modules.table_description.models import (
    ColumnDescription,
    TableDescription,
    TableDescriptionStatus,
)
from app.modules.table_description.repositories import TableDescriptionRepository
from app.modules.sql_generation.models import LLMConfig
from app.utils.model.chat_model import ChatModel
from app.utils.prompts.agent_prompts import (
    COLUMN_DESCRIPTION_PROMPT,
    TABLE_DESCRIPTION_PROMPT,
)

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 60
MAX_SIZE_LETTERS = 50

logger = logging.getLogger(__name__)


class PostgreSqlScanner:
    def cardinality_values(self, column: Column, db_engine: Engine) -> list | None:
        if str(db_engine.__dict__.get("url")).startswith("sqlite"):
            query = text(
                f"""
                WITH ValueCounts AS (
                    SELECT 
                        {column.name} AS value, 
                        COUNT(*) AS freq 
                    FROM {column.table.name}
                    GROUP BY {column.name}
                )
                SELECT 
                    (SELECT COUNT(DISTINCT {column.name}) FROM {column.table.name}) AS n_distinct,
                    json_group_array(value) AS most_common_vals
                FROM ValueCounts
                """
            )

        else:
            query = text(
                """
                SELECT n_distinct, most_common_vals::TEXT::TEXT[] 
                FROM pg_catalog.pg_stats 
                WHERE tablename = :table_name 
                AND attname = :column_name
                """
            )

        with db_engine.connect() as connection:
            result = connection.execute(
                query, {"table_name": column.table.name, "column_name": column.name}
            ).fetchall()

            if len(result) > 0:
                distinct_count, most_common_vals = result[0]
                if isinstance(most_common_vals, str):
                    most_common_vals = json.loads(most_common_vals)
                    most_common_vals = [
                        str(val) if val is not None else val for val in most_common_vals
                    ]

                if MIN_CATEGORY_VALUE <= distinct_count <= MAX_CATEGORY_VALUE:
                    return most_common_vals


class TableColumnsDescriptionGenerator:
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.model = ChatModel()

    def create_chain(self, prompt_template: str) -> Any:
        prompt = ChatPromptTemplate.from_messages([("user", prompt_template)])

        # Get the appropriate LLM model using ChatModel
        llm_model = self.model.get_model(
            database_connection=None,
            model_family=self.llm_config.model_family,
            model_name=self.llm_config.model_name,
            api_base=self.llm_config.api_base,
            temperature=0.2,
            max_retries=2,
            max_tokens=128,
        )

        return prompt | llm_model

    def generate_column_description(
        self, chain, table_name: str, columns_dict: dict, batch_size: int = 10
    ) -> dict:
        # Store final results
        column_descriptions = {}

        # Prepare column data list
        column_data_list = [
            {
                "table_name": table_name,
                "column_name": column_name,
                "row_examples": row_examples,
            }
            for column_name, row_examples in columns_dict.items()
        ]

        # Process in batches
        for i in range(0, len(column_data_list), batch_size):
            # Get current batch
            batch_items = column_data_list[i : i + batch_size]

            # Prepare inputs for batch
            batch_inputs = [
                {
                    "table_name": item["table_name"],
                    "column_name": item["column_name"],
                    "row_examples": item["row_examples"],
                }
                for item in batch_items
            ]

            # Perform LLM inference for batch
            batch_results = chain.batch(inputs=batch_inputs)

            # Collect results
            for result, item in zip(batch_results, batch_items):
                column_descriptions[item["column_name"]] = result.content

        return column_descriptions

    def get_column_description(
        self, meta: MetaData, db_engine: Engine, table: str, rows_number: int = 5
    ) -> List[Dict[str, Any]]:
        print(f"Generate column descriptions table: {table}")

        chain = self.create_chain(COLUMN_DESCRIPTION_PROMPT)

        columns = [col for col in meta.tables[table].columns if "." not in col.name]
        examples_query = sqlalchemy.select(*columns).distinct().limit(rows_number)
        with db_engine.connect() as connection:
            examples = connection.execute(examples_query).fetchall()

        # Convert query result to a dictionary
        results_dict = {col.name: [] for col in columns}

        # Populate the dictionary with distinct values
        for row in examples:
            for col, value in zip(columns, row):
                results_dict[col.name].append(value)

        columns_desc = self.generate_column_description(chain, table, results_dict)
        return columns_desc

    def get_table_description(
        self,
        table: str,
        columns_description,
    ) -> str:
        print(f"Generate table description: {table}")

        chain = self.create_chain(TABLE_DESCRIPTION_PROMPT)

        table_details = "\n".join(
            f"{key}: {value}" for key, value in columns_description.items()
        )

        table_description = chain.invoke(
            {"table_name": table, "table_details": table_details}
        ).content

        return table_description
    
    def reset_table_description(
            self,
            table_description: TableDescription,
            keep_keys: List[str]
    ) -> TableDescription:
        default_values = TableDescription(
            id=table_description.id,
            db_connection_id=table_description.db_connection_id,
            db_schema=table_description.db_schema,
            table_name=table_description.table_name,
        ).model_dump()

        for key in table_description.model_dump():
            if key not in keep_keys:
                setattr(table_description, key, default_values[key])

        return table_description

class SqlAlchemyScanner:
    def create_tables(
        self,
        tables: list[str],
        db_connection_id: str,
        schema: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> None:
        for table in tables:
            table_description = TableDescription(
                db_connection_id=db_connection_id,
                db_schema=schema,
                table_name=table,
                sync_status=TableDescriptionStatus.NOT_SCANNED.value,
                metadata=metadata,
            )
            repository.save_table_info(table_description)

    def refresh_tables(
        self,
        schemas_and_tables: dict[str, list],
        db_connection_id: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> list[TableDescription]:
        rows = []
        table_description_repo = TableColumnsDescriptionGenerator(llm_config=None)
        for schema, tables in schemas_and_tables.items():
            stored_tables = repository.find_by(
                {"db_connection_id": str(db_connection_id), "db_schema": schema}
            )
            stored_tables_list = [table.table_name for table in stored_tables]

            for table_description in stored_tables:
                table_description = table_description_repo.reset_table_description(
                    table_description,
                    keep_keys=["id", "db_connection_id", "db_schema", "table_name"]
                )
                # If source table not exist but exist in Typesense
                if table_description.table_name not in tables:
                    table_description = repository.delete_by_id(table_description.id)
                    table_description.sync_status = (
                        TableDescriptionStatus.DEPRECATED.value
                    )
                    rows.append(table_description)
                else:
                    table_description.sync_status = (
                        TableDescriptionStatus.NOT_SCANNED.value
                    )
                    rows.append(repository.save_table_info(table_description))
            
            for table in tables:
                # Add if source table not stored in Typesense
                if table not in stored_tables_list:
                    rows.append(
                        repository.save_table_info(
                            TableDescription(
                                db_connection_id=db_connection_id,
                                table_name=table,
                                sync_status=TableDescriptionStatus.NOT_SCANNED.value,
                                metadata=metadata,
                                db_schema=schema,
                            )
                        )
                    )
        return rows

    def synchronizing(
        self,
        scanner_request: ScannerRequest,
        repository: TableDescriptionRepository,
    ) -> list[TableDescription]:
        rows = []
        for id in scanner_request.table_description_ids:
            table_description = repository.find_by_id(id)
            table_info = TableDescription(
                db_connection_id=table_description.db_connection_id,
                table_name=table_description.table_name,
                sync_status=TableDescriptionStatus.SYNCHRONIZING.value,
                metadata=scanner_request.metadata,
                db_schema=table_description.db_schema,
            )
            rows.append(repository.save_table_info(table_info))

        return rows

    def get_table_examples(
        self, meta: MetaData, db_engine: Engine, table: str, rows_number: int = 3
    ) -> List[Dict[str, Any]]:
        print(f"Create examples: {table}")

        columns = [col for col in meta.tables[table].columns if "." not in col.name]
        examples_query = sqlalchemy.select(*columns).limit(rows_number)
        with db_engine.connect() as connection:
            examples = connection.execute(examples_query).fetchall()

        examples_dict = []
        columns = [column["name"] for column in examples_query.column_descriptions]
        for example in examples:
            temp_dict = {}
            for index, value in enumerate(columns):
                temp_dict[value] = str(example[index])
            examples_dict.append(temp_dict)

        return examples_dict

    def get_processed_column(  # noqa: PLR0911
        self,
        meta: MetaData,
        table_id: str,
        table_name: str,
        db_engine: Engine,
        column: dict,
        scanner_service: PostgreSqlScanner,
    ) -> ColumnDescription:
        dynamic_meta_table = meta.tables[table_name]

        column_name = column["name"]
        selected_column = dynamic_meta_table.c.get(column_name)

        field_size_query = sqlalchemy.select(selected_column).limit(1)

        with db_engine.connect() as connection:
            field_size = connection.execute(field_size_query).first()
        # Check if the column is empty
        if not field_size:
            field_size = [""]
        if len(str(str(field_size[0]))) > MAX_SIZE_LETTERS:
            column_description = ColumnDescription(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=False,
            )
            return column_description

        category_values = scanner_service.cardinality_values(
            dynamic_meta_table.c[column["name"]], db_engine
        )

        if category_values:
            column_description = ColumnDescription(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=True,
                categories=category_values,
            )
        else:
            column_description = ColumnDescription(
                name=column["name"],
                data_type=str(column["type"]),
                low_cardinality=False,
            )

        return column_description

    def get_table_schema(self, meta: MetaData, db_engine: Engine, table: str) -> str:
        print(f"Create table schema for: {table}")

        original_table = next((x for x in meta.sorted_tables if x.name == table), None)
        if original_table is None:
            raise ValueError(f"Table '{table}' not found in metadata.")

        valid_columns = []
        for col in original_table.columns:
            if isinstance(col.type, NullType):
                logger.warning(
                    f"Column {col} is ignored due to its NullType data type which is not supported"
                )
                continue
            valid_columns.append(col)

        new_columns = [
            Column(
                col.name,
                col.type,
                primary_key=col.primary_key,
                autoincrement=col.autoincrement,
            )
            for col in valid_columns
        ]

        new_table = Table(original_table.name, MetaData(), *new_columns)

        foreign_key_constraints = []
        for fk in original_table.foreign_keys:
            foreign_key_constraints.append(
                f"FOREIGN KEY (`{fk.parent.name}`) REFERENCES `{fk.column.table.name}` (`{fk.column.name}`)"
            )

        create_table_ddl = str(CreateTable(new_table).compile(db_engine.engine))
        create_table_ddl = (
            create_table_ddl.rstrip()[:-1].rstrip()
            + ",\n\t"
            + ",\n\t".join(foreign_key_constraints)
            + ");"
        )

        return create_table_ddl.rstrip()

    def delete_db_connection_tables(
        self,
        db_connection_id: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> None:
        stored_tables = repository.find_by({"db_connection_id": str(db_connection_id)})

        stored_tables_list = [table.id for table in stored_tables]

        for table_id in stored_tables_list:
            repository.delete_by_id(table_id)

    def scan_single_table(
        self,
        meta: MetaData,
        table_id: str,
        table_name: str,
        db_engine: Engine,
        db_connection_id: str,
        repository: TableDescriptionRepository,
        scanner_service: PostgreSqlScanner,
        schema: str | None = None,
        llm_config: LLMConfig = None,
    ) -> TableDescription:
        print(f"Scanning table: {table_name}")
        inspector = inspect(db_engine)
        table_columns = []
        columns = inspector.get_columns(table_name=table_name)
        columns = [column for column in columns if column["name"].find(".") < 0]

        for column in columns:
            print(f"Scanning column: {column['name']}")
            table_columns.append(
                self.get_processed_column(
                    meta=meta,
                    table_id=table_id,
                    table_name=table_name,
                    column=column,
                    db_engine=db_engine,
                    scanner_service=scanner_service,
                )
            )

        table_schema = self.get_table_schema(
            meta=meta, db_engine=db_engine, table=table_name
        )

        examples = self.get_table_examples(
            meta=meta, db_engine=db_engine, table=table_name, rows_number=3
        )

        if llm_config:
            table_columns_descriptions = TableColumnsDescriptionGenerator(llm_config)
            columns_description = table_columns_descriptions.get_column_description(
                meta=meta, db_engine=db_engine, table=table_name, rows_number=5
            )

            table_description = table_columns_descriptions.get_table_description(
                table=table_name, columns_description=columns_description
            )

            for column in table_columns:
                if column.name in columns_description:
                    # Update the description with the value from the dictionary
                    column.description = columns_description[column.name]
            print(f"Table and columns generation is DONE: {table_name}")
        else:
            table_description = columns_description = None

        object = TableDescription(
            db_connection_id=db_connection_id,
            table_name=table_name,
            table_description=table_description,
            columns=table_columns,
            examples=examples,
            table_schema=table_schema,
            last_sync=str(datetime.now()),
            error_message="",
            sync_status=TableDescriptionStatus.SCANNED.value,
            db_schema=schema,
        )

        repository.save_table_info(object)
        return object

    def scan(
        self,
        db_engine: Engine,
        table_descriptions: list[TableDescription],
        repository: TableDescriptionRepository,
        llm_config: LLMConfig = None,
    ) -> None:
        scanner_service = PostgreSqlScanner()

        inspect(db_engine)
        meta = MetaData()
        meta.reflect(bind=db_engine, views=True)

        for table in table_descriptions:
            try:
                self.scan_single_table(
                    meta=meta,
                    table_id=table.id,
                    table_name=table.table_name,
                    db_engine=db_engine,
                    db_connection_id=table.db_connection_id,
                    repository=repository,
                    scanner_service=scanner_service,
                    schema=table.db_schema,
                    llm_config=llm_config,
                )
            except Exception as e:
                raise e
                repository.save_table_info(
                    TableDescription(
                        db_connection_id=table.db_connection_id,
                        table_name=table.table_name,
                        status=TableDescriptionStatus.FAILED.value,
                        error_message=f"{e}",
                        db_schema=table.db_schema,
                    )
                )
            except Exception:  # noqa: S112
                continue

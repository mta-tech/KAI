import logging
from datetime import datetime
from typing import Any, Dict, List

import sqlalchemy
from sqlalchemy import Column, MetaData, Table, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql.sqltypes import NullType

from app.api.requests import ScannerRequest
from app.modules.table_description.models import (
    ColumnDescription,
    TableDescription,
    TableDescriptionStatus,
)
from app.modules.table_description.repositories import TableDescriptionRepository

MIN_CATEGORY_VALUE = 1
MAX_CATEGORY_VALUE = 60
MAX_SIZE_LETTERS = 50

logger = logging.getLogger(__name__)


class PostgreSqlScanner:
    def cardinality_values(self, column: Column, db_engine: Engine) -> list | None:
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
                if MIN_CATEGORY_VALUE <= distinct_count <= MAX_CATEGORY_VALUE:
                    return most_common_vals


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
        for schema, tables in schemas_and_tables.items():
            stored_tables = repository.find_by(
                {"db_connection_id": str(db_connection_id), "db_schema": schema}
            )
            stored_tables_list = [table.table_name for table in stored_tables]

            for table_description in stored_tables:
                if table_description.table_name not in tables:
                    table_description.sync_status = (
                        TableDescriptionStatus.DEPRECATED.value
                    )
                    rows.append(repository.save_table_info(table_description))
                else:
                    rows.append(TableDescription(**table_description.model_dump()))

            for table in tables:
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

        object = TableDescription(
            db_connection_id=db_connection_id,
            table_name=table_name,
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

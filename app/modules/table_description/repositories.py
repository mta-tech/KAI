from typing import List

from app.modules.table_description.models import TableDescription

DB_COLLECTION = "table_descriptions"


class TableDescriptionRepository:
    def __init__(self, storage):
        self.storage = storage

    def find_by_id(self, id: str) -> TableDescription | None:
        doc = self.storage.find_one(DB_COLLECTION, {"id": id})
        return TableDescription(**doc) if doc else None

    def get_table_info(
        self, db_connection_id: str, table_name: str
    ) -> TableDescription | None:
        doc = self.storage.find_one(
            DB_COLLECTION,
            {"db_connection_id": str(db_connection_id), "table_name": table_name},
        )
        return TableDescription(**doc) if doc else None

    def get_all_tables_by_db(self, query: dict) -> List[TableDescription]:
        rows = self.storage.find(DB_COLLECTION, query)
        tables = [TableDescription(**row) for row in rows]
        return tables

    def save_table_info(self, table_info: TableDescription) -> TableDescription:
        table_info_dict = table_info.model_dump(exclude={"id"})
        table_info_dict["table_name"] = table_info.table_name.lower()
        table_info_dict = {
            k: v for k, v in table_info_dict.items() if v is not None and v != []
        }

        filter = {
            "db_connection_id": table_info_dict["db_connection_id"],
            "table_name": table_info_dict["table_name"],
        }
        if "table_schema" in table_info_dict:
            filter["table_schema"] = table_info_dict["table_schema"]

        table_info.id = str(
            self.storage.update_or_create(
                DB_COLLECTION,
                filter,
                table_info_dict,
            )
        )
        return table_info

    def update(self, table_info: TableDescription) -> TableDescription:
        table_info_dict = table_info.model_dump(exclude={"id"})
        table_info_dict = {
            k: v for k, v in table_info_dict.items() if v is not None and v != []
        }
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": table_info.id},
            table_info_dict,
        )
        return table_info

    def find_all(self) -> list[TableDescription]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = [TableDescription(**row) for row in rows]
        return result

    def find_by(self, query: dict) -> list[TableDescription]:
        query = {k: v for k, v in query.items() if v}
        rows = self.storage.find(DB_COLLECTION, query)
        result = []
        for row in rows:
            obj = TableDescription(**row)
            obj.columns = sorted(obj.columns, key=lambda x: x.name)
            result.append(obj)
        return result

    def update_fields(self, table: TableDescription, table_description_request):
        if table_description_request.description is not None:
            table.description = table_description_request.description

        if table_description_request.metadata is not None:
            table.metadata = table_description_request.metadata

        if table_description_request.columns:
            columns = [column.name for column in table.columns]

            for column_request in table_description_request.columns:
                if column_request.name not in columns:
                    raise Exception(
                        f"Column {column_request.name} doesn't exist"
                    )
                for column in table.columns:
                    if column_request.name == column.name:
                        for field, value in column_request:
                            if value is None or value == []:
                                continue
                            setattr(column, field, value)
        return self.update(table)

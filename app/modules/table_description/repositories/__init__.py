from typing import List

from fastapi import HTTPException

from app.data.db.storage import Storage
from app.modules.table_description.models import TableDescription

DB_COLLECTION = "table_descriptions"


class TableDescriptionRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def find_by_id(self, id: str) -> TableDescription | None:
        doc = self.storage.find_one(DB_COLLECTION, {"id": id})
        if doc:
            return TableDescription(**doc)
        return None

    def get_table_info(
        self, db_connection_id: str, table_name: str
    ) -> TableDescription | None:
        # search table description by its name and all the columns realted to the table
        doc = self.storage.find_one(
            DB_COLLECTION,
            {"db_connection_id": str(db_connection_id), "table_name": table_name},
        )
        return TableDescription(**doc) if doc else None

    def get_all_tables_by_db(self, filter: dict) -> List[TableDescription]:
        rows = self.storage.find(DB_COLLECTION, filter)
        tables = [TableDescription(**row) for row in rows]
        return tables

    def save_table_info(self, table_info: TableDescription) -> TableDescription:
        table_info_dict = table_info.model_dump(exclude={"id"})
        table_info_dict["table_name"] = table_info.table_name

        filter = {
            "db_connection_id": table_info_dict["db_connection_id"],
            "table_name": table_info_dict["table_name"],
        }
        if table_info_dict["db_schema"]:
            filter["db_schema"] = table_info_dict["db_schema"]

        # Save table info
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
        # get all table description and its columns
        rows = self.storage.find_all(DB_COLLECTION)
        result = [TableDescription(**row) for row in rows]
        return result

    def find_by(self, filter: dict) -> list[TableDescription]:
        filter = {k: v for k, v in filter.items() if v}
        rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            obj = TableDescription(**row)
            result.append(obj)
        return result

    def update_fields(self, table: TableDescription, table_description_request):
        if table_description_request.table_description is not None:
            table.table_description = table_description_request.table_description

        if table_description_request.metadata is not None:
            table.metadata = table_description_request.metadata

        if table_description_request.columns:
            columns = [column.name for column in table.columns]

            for column_request in table_description_request.columns:
                if column_request.name not in columns:
                    raise HTTPException(f"Column {column_request.name} doesn't exist")
                for column in table.columns:
                    if column_request.name == column.name:
                        for field, value in column_request:
                            if value is None or value == []:
                                continue
                            setattr(column, field, value)
        return self.update(table)

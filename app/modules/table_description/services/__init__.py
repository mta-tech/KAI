from fastapi import BackgroundTasks, HTTPException

from app.api.requests import ScannerRequest, TableDescriptionRequest
from app.api.responses import TableDescription
from app.data.db.storage import Storage
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.table_description.repositories import TableDescriptionRepository
from app.utils.sql_database.scanner import SqlAlchemyScanner


def async_scanning(scanner: SqlAlchemyScanner, engine, table_descriptions, storage):
    scanner.scan(engine, table_descriptions, TableDescriptionRepository(storage))


class TableDescriptionService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> list[TableDescription]:
        """Takes a table_description_id and scan all the tables columns"""
        scanner_repository = TableDescriptionRepository(self.storage)
        data = {}
        for table_id in scanner_request.table_description_ids:
            table_description = scanner_repository.find_by_id(table_id)
            if not table_description:
                raise HTTPException("Table description not found")
            if table_description.db_connection_id not in data.keys():
                data[table_description.db_connection_id] = {}
            if (
                table_description.db_schema
                not in data[table_description.db_connection_id].keys()
            ):
                data[table_description.db_connection_id][
                    table_description.db_schema
                ] = []
            data[table_description.db_connection_id][
                table_description.db_schema
            ].append(table_description)

        db_connection_repository = DatabaseConnectionRepository(self.storage)

        scanner = SqlAlchemyScanner()
        rows = scanner.synchronizing(
            scanner_request,
            TableDescriptionRepository(self.storage),
        )

        database_connection_service = DatabaseConnectionService(scanner, self.storage)
        for db_connection_id, schemas_and_table_descriptions in data.items():
            for schema, table_descriptions in schemas_and_table_descriptions.items():
                db_connection = db_connection_repository.find_by_id(db_connection_id)

                database = database_connection_service.get_sql_database(
                    db_connection, schema
                )

                engine = database.engine

                background_tasks.add_task(
                    async_scanning, scanner, engine, table_descriptions, self.storage
                )
        return [TableDescription(**row.model_dump()) for row in rows]

    def refresh_table_description(
        self, database_connection_id: str
    ) -> list[TableDescription]:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(database_connection_id)
        scanner = SqlAlchemyScanner()
        database_connection_service = DatabaseConnectionService(self.storage)
        try:
            data = {}
            if db_connection.schemas:
                for schema in db_connection.schemas:
                    sql_database = database_connection_service.get_sql_database(
                        db_connection, schema
                    )
                    if schema not in data.keys():
                        data[schema] = []
                    data[schema] = sql_database.get_tables_and_views()
            else:
                sql_database = database_connection_service.get_sql_database(
                    db_connection
                )
                data[None] = sql_database.get_tables_and_views()

            scanner_repository = TableDescriptionRepository(self.storage)

            return [
                TableDescription(**record.model_dump())
                for record in scanner.refresh_tables(
                    data, str(db_connection.id), scanner_repository
                )
            ]
        except Exception as e:
            raise e

    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableDescription:
        scanner_repository = TableDescriptionRepository(self.storage)
        try:
            table = scanner_repository.find_by_id(table_description_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not table:
            raise HTTPException(
                status_code=404, detail="Scanned database table not found"
            )

        try:
            table_description = scanner_repository.update_fields(
                table, table_description_request
            )
            return TableDescription(**table_description.model_dump())
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    def get_table_description(self, table_description_id: str) -> TableDescription:
        scanner_repository = TableDescriptionRepository(self.storage)

        result = scanner_repository.find_by_id(table_description_id)

        if result is None:
            raise HTTPException(status_code=404, detail="Table description not found")

        return TableDescription(**result.model_dump())

    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescription]:
        table_description_repository = TableDescriptionRepository(self.storage)
        table_descriptions = table_description_repository.find_by(
            {"db_connection_id": str(db_connection_id), "table_name": table_name}
        )
        return [
            TableDescription(**table_description.model_dump())
            for table_description in table_descriptions
        ]

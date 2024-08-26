import fastapi
from fastapi import BackgroundTasks

from app.api.requests import DatabaseConnectionRequest, ScannerRequest
from app.api.responses import DatabaseConnectionResponse, TableDescriptionResponse
from app.data.db.storage import Storage
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.table_description.services import TableDescriptionService

class API:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.router = fastapi.APIRouter()
        self.database_connection_service = DatabaseConnectionService(self.storage)
        self.table_description_service = TableDescriptionService(self.storage)

        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/api/v1/database-connections",
            self.create_database_connection,
            methods=["POST"],
            status_code=201,
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections",
            self.list_database_connections,
            methods=["GET"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections/{db_connection_id}",
            self.update_database_connection,
            methods=["PUT"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/sync-schemas",
            self.scan_db,
            methods=["POST"],
            status_code=201,
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/refresh",
            self.refresh_table_description,
            methods=["POST"],
            status_code=201,
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.update_table_description,
            methods=["PUT"],
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions",
            self.list_table_descriptions,
            methods=["GET"],
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.get_table_description,
            methods=["GET"],
            tags=["Table Descriptions"],
        )

    def get_router(self) -> fastapi.APIRouter:
        return self.router

    def create_database_connection(
        self, request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        return self.database_connection_service.create_database_connection(request)

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        return self.database_connection_service.list_database_connections()

    def update_database_connection(
        self,
        db_connection_id: str,
        request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return self.database_connection_service.update_database_connection(
            db_connection_id, request
        )

    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> list[TableDescriptionResponse]:
        return self.table_description_service.scan_db(scanner_request, background_tasks)

    def refresh_table_description(
        self, database_connection_id: str
    ) -> list[TableDescriptionResponse]:
        return self.table_description_service.refresh_table_description(
            database_connection_id
        )

    def update_table_description(
        self,
        table_description_id: str,
        database_connection_id: str,
    ) -> TableDescriptionResponse:
        """Add descriptions for tables and columns"""
        return self.table_description_service.update_table_description(
            table_description_id, database_connection_id
        )

    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescriptionResponse]:
        """List table descriptions"""
        return self.table_description_service.list_table_descriptions(
            db_connection_id, table_name
        )

    def get_table_description(
        self, table_description_id: str
    ) -> TableDescriptionResponse:
        """Get description"""
        return self.table_description_service.get_table_description(
            table_description_id
        )

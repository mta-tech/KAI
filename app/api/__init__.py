import fastapi

from app.api.requests import (
    DatabaseConnectionRequest,
)
from app.api.responses import (
    DatabaseConnectionResponse,
)
from app.data.db.storage import Storage
from app.modules.database_connection.services import DatabaseConnectionService


class API:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.router = fastapi.APIRouter()
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

    def get_router(self) -> fastapi.APIRouter:
        return self.router

    def create_database_connection(
        self, request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        return DatabaseConnectionService().create_database_connection(request)

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        return DatabaseConnectionService().list_database_connections()

    def update_database_connection(
        self,
        db_connection_id: str,
        request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return DatabaseConnectionService().update_database_connection(
            db_connection_id, request
        )

from fastapi import APIRouter

from app.data import Storage
from app.routers.endpoints import Endpoint
from app.routers.schemas.request import DatabaseConnectionRequest
from app.routers.schemas.response import DatabaseConnectionResponse
from app.server.config import Settings
from app.services.database_connection import DatabaseConnectionService


class DatabaseConnectionRouter(Endpoint):
    def __init__(self, settings: Settings, storage: Storage):
        super().__init__(settings, storage)
        self._service = DatabaseConnectionService(settings, storage)
        self._router = APIRouter(prefix="/api/v1/database-connections")

        self._router.add_api_route(
            path="",
            endpoint=self.list_database_connections,
            methods=["GET"],
            tags=["Database Connections"],
        )

        self._router.add_api_route(
            path="",
            endpoint=self.create_database_connections,
            methods=["POST"],
            tags=["Database Connections"],
        )

        self._router.add_api_route(
            path="/{db_connection_id}",
            endpoint=self.update_database_connections,
            methods=["PUT"],
            tags=["Database Connections"],
        )

        self._router.add_api_route(
            path="/{db_connection_id}",
            endpoint=self.delete_database_connections,
            methods=["DELETE"],
            tags=["Database Connections"],
        )

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        return self._service.list_database_connections()

    def create_database_connections(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        return self._service.create_database_connection(database_connection_request)

    def update_database_connections(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return self._service.update_database_connections(
            db_connection_id, database_connection_request
        )

    def delete_database_connections(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return self._service.delete_database_connections(
            db_connection_id, database_connection_request
        )

    def router(self):
        return self._router

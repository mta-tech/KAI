from fastapi import APIRouter

from app.api.schemas.request import DatabaseConnectionRequest
from app.api.schemas.response import DatabaseConnectionResponse
from app.services.database_connection import DatabaseConnectionService


class DatabaseConnectionRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/database-connections")

        self.router.add_api_route(
            path="",
            endpoint=self.list_database_connections,
            methods=["GET"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            path="",
            endpoint=self.create_database_connections,
            methods=["POST"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            path="/{db_connection_id}",
            endpoint=self.update_database_connections,
            methods=["PUT"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            path="/{db_connection_id}",
            endpoint=self.delete_database_connections,
            methods=["DELETE"],
            tags=["Database Connections"],
        )

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        return DatabaseConnectionService().list_database_connections()

    def create_database_connections(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        return DatabaseConnectionService().create_database_connection(
            database_connection_request
        )

    def update_database_connections(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return DatabaseConnectionService().update_database_connections(
            db_connection_id, database_connection_request
        )

    def delete_database_connections(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return DatabaseConnectionService().delete_database_connections(
            db_connection_id, database_connection_request
        )

    def get_router(self):
        return self.router

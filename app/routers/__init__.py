import fastapi

from app.data import Storage
from app.routers.endpoints.database_connection import DatabaseConnectionRouter


class Router:
    def __init__(self, storage: Storage):
        self._router = fastapi.APIRouter()

        self._service_routes = [
            DatabaseConnectionRouter(storage).router(),
        ]

        self.include_router()

    def include_router(self):
        for route in self._service_routes:
            self._router.include_router(route)

    def router(self) -> fastapi.APIRouter:
        return self._router

import fastapi

from app.data import Storage
from app.routers.endpoints.database_connection import DatabaseConnectionRouter
from app.server.config import Settings


class Router:
    def __init__(self, settings: Settings, storage: Storage):
        self._router = fastapi.APIRouter()

        self._service_routes = [
            DatabaseConnectionRouter(settings, storage).router(),
        ]

        self.include_router()

    def include_router(self):
        for route in self._service_routes:
            self._router.include_router(route)

    def router(self) -> fastapi.APIRouter:
        return self._router

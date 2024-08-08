import fastapi
from app.api.endpoints.database_connection import DatabaseConnectionRouter
from app.api.endpoints.database_connection import DatabaseScannerRouter


class Router:
    def __init__(self):
        self._router = fastapi.APIRouter()

        self._router.include_router(DatabaseConnectionRouter().get_router())
        self._router.include_router(DatabaseScannerRouter().get_router())


    def router(self) -> fastapi.APIRouter:
        return self._router
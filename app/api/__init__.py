import fastapi
from app.api.endpoints.database_connection import DatabaseConnectionRouter


class Router:
    def __init__(self):
        self._router = fastapi.APIRouter()

        self._router.include_router(DatabaseConnectionRouter().get_router())


    def router(self) -> fastapi.APIRouter:
        return self._router
import fastapi
from app.api import API

from app.data.db.storage import Storage
from app.server.config import Settings
from app.utils.sql_database.sql_database import DBConnections


class FastAPI:
    def __init__(self, settings: Settings):
        self._storage = Storage(settings)
        self._app = fastapi.FastAPI(
            debug=True,
            title=settings.APP_NAME,
            description=settings.APP_DESCRIPTION,
            version=settings.APP_VERSION,
        )

        self._api = API(self._storage)
        self._app.include_router(self._api.get_router())

        @self._app.on_event("shutdown")
        async def shutdown_event():
            DBConnections.dispose_all_engines()

    def app(self) -> fastapi.FastAPI:
        return self._app

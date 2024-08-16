import os

import fastapi

from app.data import Storage
from app.routers import Router
from app.server.config import Settings


class FastAPI:
    def __init__(self, settings: Settings):
        self._storage = Storage(settings)

        self._router = Router(self._storage)

        self._app = fastapi.FastAPI(
            debug=True,
            title=settings.APP_NAME,
            description=settings.APP_DESCRIPTION,
            version=settings.APP_VERSION,
        )

        self._app.include_router(self._router.router())

    def app(self) -> fastapi.FastAPI:
        return self._app

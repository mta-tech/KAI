import os

import fastapi
from fastapi import APIRouter

from app.core.config import Settings
from app.storage.schemas import SchemaInitialization

FLAG_FILE = "initialized.flag"


class FastAPI:
    def __init__(self, settings: Settings, router: APIRouter):
        self._app = fastapi.FastAPI(
            debug=True,
            title=settings.APP_NAME,
            # description=settings.APP_DESCRIPTION,
            version=settings.APP_VERSION,
        )
        self._router = router
        self._app.include_router(self._router)

        self.initialize_database()

    def initialize_database(self):
        if not os.path.exists(FLAG_FILE):
            SchemaInitialization.initialize()
            with open(FLAG_FILE, "w") as file:
                file.write("Database initialized")

    def app(self) -> fastapi.FastAPI:
        return self._app

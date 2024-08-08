import fastapi
from fastapi import APIRouter

from app.core.config import Settings


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

    def app(self) -> fastapi.FastAPI:
        return self._app

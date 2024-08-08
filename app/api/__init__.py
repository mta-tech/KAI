import fastapi
from fastapi import APIRouter

class FastAPI():
    def __init__(self, router: APIRouter):
        self._app = fastapi.FastAPI(debug=True)
        self._router = router
        self._app.include_router(self._router)

    def app(self) -> fastapi.FastAPI:
        return self._app

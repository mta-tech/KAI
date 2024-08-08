from app.core.config import Settings
from app.api import FastAPI
from app.api.endpoints import Router
from uvicorn import run

settings = Settings()
router = Router().router()
server = FastAPI(router)
app = server.app()

if __name__ == "__main__":
    run(
        app="app.server:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload= settings.APP_ENABLE_HOT_RELOAD,
    )

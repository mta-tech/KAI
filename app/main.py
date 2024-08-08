from uvicorn import run

from app.server import FastAPI
from app.api import Router
from app.core.config import Settings

settings = Settings()
router = Router().router()
server = FastAPI(settings, router)
app = server.app()

if __name__ == "__main__":
    run(
        app="app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENABLE_HOT_RELOAD,
    )

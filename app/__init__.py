from uvicorn import run

from app.server import FastAPI
from app.server.config import Settings

settings = Settings()
server = FastAPI(settings)
app = server.app()

if __name__ == "__main__":
    run(
        app="app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENABLE_HOT_RELOAD,
    )

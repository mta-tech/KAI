from app.core.config import Settings
from app.api import FastAPI
from app.api.endpoints import Router
from uvicorn import run


router = Router().router()
server = FastAPI(router)
app = server.app()


if __name__ == "__main__":
    run(
        app=app,
        host=Settings.APP_HOST,
        port=Settings.APP_PORT,
        reload=Settings.APP_ENABLE_HOT_RELOAD,
    )

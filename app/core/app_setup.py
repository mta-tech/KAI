from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.logging_config import setup_logging

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI()
    
    # Setup middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Example setting
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Other setup tasks (e.g., event handlers)
    @app.on_event("startup")
    async def on_startup():
        print("Application is starting...")
    
    @app.on_event("shutdown")
    async def on_shutdown():
        print("Application is shutting down...")
    
    return app

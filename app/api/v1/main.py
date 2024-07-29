# app/api/v1/main.py

from fastapi import FastAPI
from app.core.app_setup import create_app  # Import app setup function
from .endpoints import init  # Import the API router

app = FastAPI()

# Setup the application (including middleware, startup events, etc.)
create_app(app)

# Include the API router
app.include_router(init.router, prefix="/v1")

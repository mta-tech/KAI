from fastapi import APIRouter

from . import users, items  # Import the routers

router = APIRouter()

# Include routers for users and items
router.include_router(users.router, prefix="/v1", tags=["users"])
router.include_router(items.router, prefix="/v1", tags=["items"])

from fastapi import APIRouter, HTTPException
from typing import List
from app.api.v1.schemas.request import UserCreateRequest
from app.api.v1.schemas.response import UserResponse
from app.services import user_service  # Assuming user_service handles business logic

router = APIRouter()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreateRequest):
    """
    Create a new user.
    """
    user_id = user_service.create_user(user)
    if user_id is None:
        raise HTTPException(status_code=400, detail="User creation failed")
    return {"user_id": user_id, **user.dict()}

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """
    Retrieve a user by ID.
    """
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

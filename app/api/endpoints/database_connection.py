from fastapi import APIRouter
from app.modules.database_connection.services import DatabaseConnection 
from app.api.schemas.request.database_connection import CreateRequest 
from app.api.schemas.response.database_connection import CreateResponse

class DatabaseConnectionRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/database-connection")
        
        self.router.add_api_route(
            path= "/",
            endpoint= self.create_db_connection,
            methods=["POST"],
            tags=["database_connection"]
        )
    
    def create_db_connection(self, request: CreateRequest) -> CreateResponse:
        return DatabaseConnection.create_db_connection(request)
    
    def get_router(self):
        return self.router
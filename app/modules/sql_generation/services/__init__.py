from app.modules.sql_generation.models import SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.modules.sql_generation.services.sql_generations import SQLGenerationService
from app.server.errors import error_response

class SQLGenerationService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = SQLGenerationRepository(storage)

    def create_sql_generation(
        self, prompt_id: str, sql_generation_request
    ) -> SQLGeneration:
        ObjectId(prompt_id)
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        sql_generation = sql_generation_service.create(
            prompt_id, sql_generation_request
        )

        try:
            ObjectId(prompt_id)
            sql_generation_service = SQLGenerationService(self.system, self.storage)
            sql_generation = sql_generation_service.create(
                prompt_id, sql_generation_request
            )
        except Exception as e:
            return error_response(
                e, sql_generation_request.dict(), "sql_generation_not_created"
            )
        
        return SQLGeneration(**sql_generation.dict())

from app.modules.sql_generation.repositories import SQLGenerationRepository


class SQLGenerationService:
    def __init__(self, storage):
        self.storage = storage
        self.sql_generation_repository = SQLGenerationRepository(storage)

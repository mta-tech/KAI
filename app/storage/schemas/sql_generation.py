from app.storage.typesense import TypeSenseDB

class SQLGenerationSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "sql_generation",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "prompt_id", "type": "string"},
                {"name": "llm_name", "type": "string"},
                {"name": "evaluate", "type": "bool"},
                {"name": "evaluation_score", "type": "int32"},
                {"name": "status", "type": "string"},
                {"name": "sql", "type": "string"},
                {"name": "error_message", "type": "string"},
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "created_at", "type": "string"},
                {"name": "completed_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)
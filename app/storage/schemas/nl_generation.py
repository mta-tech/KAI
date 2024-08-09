from app.storage.typesense import TypeSenseDB


class NLGenerationSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "nl_generation",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "sql_generation_id", "type": "string"},
                {"name": "llm_name", "type": "string"},
                {"name": "text", "type": "string"},
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "created_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)

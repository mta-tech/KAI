from app.storage.typesense import TypeSenseDB

class PromptSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "prompt",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "db_connection_id", "type": "string"},
                {"name": "text", "type": "string"},
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "created_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)
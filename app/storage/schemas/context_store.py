from app.storage.typesense import TypeSenseDB


class ContextStoreSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "context_store",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "db_connection_id", "type": "string"},
                {"name": "prompt_text", "type": "string"},
                {
                    "name": "prompt_embedding",
                    "type": "float[]",
                    "embed": {
                        "from": ["prompt_text"],
                        "model_config": {"model_name": "ts/all-MiniLM-L12-v2"},
                    },
                },
                {"name": "sql", "type": "string"},
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "created_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)

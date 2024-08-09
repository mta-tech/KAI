from app.storage.typesense import TypeSenseDB


class TableDescriptionSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "table_description",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "db_connection_id", "type": "string"},
                {"name": "db_schema", "type": "string"},
                {"name": "table_name", "type": "string"},
                {
                    "name": "table_embedding",
                    "type": "float[]",
                    "embed": {
                        "from": ["table_name"],
                        "model_config": {"model_name": "ts/all-MiniLM-L12-v2"},
                    },
                },
                {"name": "table_description", "type": "string"},
                {"name": "sync_status", "type": "string"},
                {"name": "table_schema", "type": "string"},
                {"name": "error_message", "type": "string"},
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "last_sync", "type": "string"},
                {"name": "created_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)

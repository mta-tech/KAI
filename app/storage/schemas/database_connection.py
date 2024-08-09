from app.storage.typesense import TypeSenseDB


class DatabaseConnectionSchema:
    def __init__(self):
        self.collection_schema = {
            "name": "database_connection",
            "enable_nested_fields": True,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "alias", "type": "string"},
                {"name": "dialect", "type": "string"},
                {"name": "connection_uri", "type": "string"},
                {"name": "schemas", "type": "string[]"},
                {"name": "metadata", "type": "object", "optional": True},
                {"name": "created_at", "type": "string"},
            ],
        }
        TypeSenseDB.create_collection(self.collection_schema)

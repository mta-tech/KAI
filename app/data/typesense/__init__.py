import json
import os

import typesense

from app.server.config import Settings


class TypeSenseDB:
    def __init__(self, setting: Settings) -> None:
        self.client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": setting.TYPESENSE_HOST,
                        "port": setting.TYPESENSE_PORT,
                        "protocol": setting.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": setting.TYPESENSE_API_KEY,
                "connection_timeout_seconds": setting.TYPESENSE_TIMEOUT,
            }
        )

        self.schema_path = "app/data/typesense/schemas"

    def get_schema(self, collection_name):
        file_path = f"{self.schema_path}/{collection_name}.json"
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Schema not found for collection: {collection_name}"
            )
        with open(file_path) as f:
            collection_schema = json.load(f)

        return collection_schema

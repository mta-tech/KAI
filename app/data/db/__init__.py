import json
import os

import typesense

from app.server.config import Settings


class TypeSenseDB:
    def __init__(self, setting: Settings):
        self.client = self._initialize_client(setting)
        self.schema_path = "app/data/db/schemas"

    def _initialize_client(self, setting: Settings) -> typesense.Client:
        """Initialize the Typesense client."""
        return typesense.Client(
            {
                "nodes": [
                    {
                        "host": setting.TYPESENSE_HOST,
                        "port": setting.TYPESENSE_PORT,
                        "protocol": setting.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": setting.TYPESENSE_API_KEY,
                # "connection_timeout_seconds": setting.TYPESENSE_TIMEOUT,
            }
        )

    def _get_schema(self, collection_name: str) -> dict:
        """Retrieve and parse the schema for a given collection."""
        file_path = os.path.join(self.schema_path, f"{collection_name}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Schema not found for collection: {collection_name}"
            )
        with open(file_path, "r") as schema_file:
            return json.load(schema_file)

    def _get_existing_collections(self) -> set:
        """Retrieve the set of existing collection names."""
        return [col["name"] for col in self.client.collections.retrieve()]

    def ensure_collection_exists(self, collection_name: str) -> None:
        """Ensure the collection exists in Typesense; if not, create it."""
        existing_collection = self._get_existing_collections()
        if collection_name not in existing_collection:
            collection_schema = self._get_schema(collection_name)
            self.client.collections.create(collection_schema)

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from Typesense."""
        self.client.collections[collection_name].delete()
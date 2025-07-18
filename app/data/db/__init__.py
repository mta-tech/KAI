import json
import os

import typesense

# from app.server.config import Settings


class TypeSenseDB:
    def __init__(self, setting):
        self.client = self._initialize_client(setting)
        self.embedding_dimensions = setting.EMBEDDING_DIMENSIONS
        self.schema_path = "app/data/db/schemas"

    def _initialize_client(self, setting) -> typesense.Client:
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

    def _add_embedding_dimensions(self, schema: dict) -> dict:
        num_dim = self.embedding_dimensions
        for field in schema.get("fields", []):
            if "embedding" in field["name"]:
                try:  # Try to set num_dim value to embedding field
                    field["num_dim"] = num_dim
                except Exception as e:
                    print(e, field)

        return schema

    def ensure_collection_exists(self, collection_name: str) -> None:
        """Ensure the collection exists in Typesense; if not, create it."""
        existing_collection = self._get_existing_collections()
        if collection_name not in existing_collection:
            collection_schema = self._get_schema(collection_name)
            collection_schema = self._add_embedding_dimensions(collection_schema)
            self.client.collections.create(collection_schema)

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from Typesense."""
        self.client.collections[collection_name].delete()

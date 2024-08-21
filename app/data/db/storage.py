from app.data.db import TypeSenseDB
from app.server.config import Settings


class Storage(TypeSenseDB):
    def __init__(self, setting: Settings) -> None:
        super().__init__(setting)

    def find_one(self, collection: str, filter: dict) -> dict:
        self.ensure_collection_exists(collection)

        filter_string = " && ".join(f"{key}:'{value}'" for key, value in filter.items())

        search_params = {"q": "*", "filter_by": filter_string}

        results = self.client.collections[collection].documents.search(search_params)
        return results.get("hits", [{}])[0]

    def insert_one(self, collection: str, doc: dict) -> int:
        self.ensure_collection_exists(collection)
        created_id = self.client.collections[collection].documents.create(doc)["id"]
        return created_id

    def update_or_create(self, collection: str, filter: dict, doc: dict) -> dict:
        self.ensure_collection_exists(collection)
        existing_doc = self.find_one(collection, filter)

        if existing_doc:
            document_id = existing_doc["id"]
            if "created_at" in doc:
                del doc["created_at"]
            self.client.collections[collection].documents[document_id].update(doc)
            return document_id
        else:
            return self.insert_one(collection, doc)

    def find_by_id(self, collection: str, id: str) -> dict:
        self.ensure_collection_exists(collection)
        results = self.client.collections[collection].documents.search(
            {"filter_by": f"id:={id}"}
        )
        if results["found"] > 0:
            return results["hits"][0]["document"]
        return None

    def find(
        self,
        collection: str,
        filter: dict,
        sort: list = None,
        page: int = 0,
        limit: int = 0,
    ) -> list:
        self.ensure_collection_exists(collection)

        filter_by = " && ".join([f"{k}:={v}" for k, v in filter.items()])

        search_params = {
            "filter_by": filter_by,
            "per_page": limit if limit > 0 else 250,
            "page": page if page > 0 else 1,
        }

        if sort:
            search_params["sort_by"] = ",".join(sort)

        results = self.client.collections[collection].documents.search(search_params)
        return [hit["document"] for hit in results["hits"]]

    def find_all(self, collection: str, page: int = 0, limit: int = 0) -> list:
        self.ensure_collection_exists(collection)

        search_params = {
            "per_page": limit if limit > 0 else 250,
            "page": page if page > 0 else 1,
        }

        results = self.client.collections[collection].documents.search(search_params)
        return [hit["document"] for hit in results["hits"]]

    def delete_by_id(self, collection: str, id: str) -> int:
        self.ensure_collection_exists(collection)
        deleted_count = (
            1 if self.client.collections[collection].documents[id].delete() else 0
        )
        return deleted_count

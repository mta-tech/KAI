import uuid

from app.data.db import TypeSenseDB
from app.server.config import Settings


class Storage(TypeSenseDB):
    def __init__(self, setting: Settings) -> None:
        super().__init__(setting)

    def find_one(self, collection: str, filter: dict) -> dict:
        self.ensure_collection_exists(collection)

        filter_string = " && ".join(f"{key}:{value}" for key, value in filter.items())

        search_params = {"q": "*", "filter_by": filter_string}

        results = self.client.collections[collection].documents.search(search_params)
        if results["found"] > 0:
            return results["hits"][0]["document"]
        return None

    def insert_one(self, collection: str, doc: dict) -> int:
        self.ensure_collection_exists(collection)
        doc["id"] = str(uuid.uuid4())
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
        search_params = {
            "q": "*",
            "filter_by": f"id:={id}",
        }

        results = self.client.collections[collection].documents.search(search_params)

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
            "q": "*",
            "filter_by": filter_by,
            "per_page": limit if limit > 0 else 250,
            "page": page if page > 0 else 1,
        }

        if sort:
            search_params["sort_by"] = ",".join(sort)

        results = self.client.collections[collection].documents.search(search_params)
        return [hit["document"] for hit in results["hits"]]

    def find_all(
        self,
        collection: str,
        page: int = 0,
        limit: int = 0,
        exclude_fields: list[str] = None,
    ) -> list:
        self.ensure_collection_exists(collection)

        search_params = {
            "q": "*",
            "per_page": limit if limit > 0 else 250,
            "page": page if page > 0 else 1,
        }

        if exclude_fields:
            search_params["exclude_fields"] = ",".join(exclude_fields)

        results = self.client.collections[collection].documents.search(search_params)
        return [hit["document"] for hit in results["hits"]]

    def full_text_search(
        self,
        collection: str,
        query: str,
        columns: list,
    ):
        self.ensure_collection_exists(collection)
        query_by = ",".join(columns)

        search_params = {"q": query, "query_by": query_by}

        results = self.client.collections[collection].documents.search(search_params)
        return [hit["document"] for hit in results["hits"]]

    def hybrid_search(
        self,
        collection: str,
        query: str,
        query_by: str,
        vector_query: str,
        exclude_fields: str,
        filter_by: str = None,
        limit: int = 3,
    ) -> list | None:
        search_requests = {
            "searches": [
                {
                    "collection": collection,
                    "q": query,
                    "query_by": query_by,
                    "vector_query": vector_query,
                    "exclude_fields": exclude_fields,
                }
            ]
        }

        common_search_params = {}
        if filter_by:
            common_search_params["filter_by"] = filter_by

        results = self.client.multi_search.perform(
            search_requests, common_search_params
        )

        if results["results"][0]["found"] > 0:
            hits = results["results"][0]["hits"]
            # Sort results by rank_fusion_score desc
            sorted_hits = sorted(
                hits,
                key=lambda x: x["hybrid_search_info"]["rank_fusion_score"],
                reverse=True,
            )
            # Take top N results
            sorted_hits = sorted_hits[:limit]

            return [
                {
                    **hit["document"],
                    "score": hit["hybrid_search_info"]["rank_fusion_score"],
                }
                for hit in sorted_hits
            ]

        return None

    def delete_by_id(self, collection: str, id: str) -> int:
        self.ensure_collection_exists(collection)
        deleted_count = (
            1 if self.client.collections[collection].documents[id].delete() else 0
        )
        return deleted_count

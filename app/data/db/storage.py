import uuid

from app.data.db import TypeSenseDB
# from app.server.config import Settings

# Typesense has a 4000 character limit for query strings
MAX_TYPESENSE_QUERY_LENGTH = 3900
# Max length for individual filter values to stay under query limit
MAX_FILTER_VALUE_LENGTH = 500


class Storage(TypeSenseDB):
    def __init__(self, setting) -> None:
        super().__init__(setting)

    def _escape_filter_value(self, value, truncate: bool = True) -> str:
        """Escape filter values for Typesense - wrap strings in backticks.

        Args:
            value: The value to escape
            truncate: If True, truncate long strings to avoid 4000 char limit
        """
        if isinstance(value, bool):
            # Booleans must be lowercase true/false without quotes
            return "true" if value else "false"
        if isinstance(value, str):
            # Check if it's a string representation of a boolean
            if value.lower() in ("true", "false"):
                return value.lower()
            # Truncate long strings to avoid Typesense 4000 char limit
            if truncate and len(value) > MAX_FILTER_VALUE_LENGTH:
                value = value[:MAX_FILTER_VALUE_LENGTH]
            # Escape backticks within the value and wrap in backticks
            escaped = value.replace('`', '\\`')
            return f"`{escaped}`"
        return str(value)

    def _truncate_query(self, query: str) -> str:
        """Truncate query to avoid Typesense 4000 char limit."""
        if len(query) > MAX_TYPESENSE_QUERY_LENGTH:
            return query[:MAX_TYPESENSE_QUERY_LENGTH]
        return query

    def find_one(self, collection: str, filter: dict) -> dict:
        self.ensure_collection_exists(collection)

        filter_string = " && ".join(
            f"{key}:{self._escape_filter_value(value)}" for key, value in filter.items()
        )

        search_params = {"q": "*", "filter_by": filter_string}

        results = self.client.collections[collection].documents.search(search_params)
        if results["found"] > 0:
            return results["hits"][0]["document"]
        return None

    def find_exactly_one(self, collection: str, filter: dict) -> dict:
        self.ensure_collection_exists(collection)

        filter_string = " && ".join(
            f"{key}:={self._escape_filter_value(value)}" for key, value in filter.items()
        )

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

    def upsert(self, collection: str, doc: dict) -> str:
        """Insert or update a document by its ID.

        Args:
            collection: Collection name
            doc: Document to upsert (must contain 'id' field)

        Returns:
            Document ID
        """
        self.ensure_collection_exists(collection)
        result = self.client.collections[collection].documents.upsert(doc)
        return result["id"]

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

        filter_by = " && ".join(
            [f"{k}:={self._escape_filter_value(v)}" for k, v in filter.items()]
        )

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

        # Truncate query to avoid Typesense 4000 char limit
        truncated_query = self._truncate_query(query)

        search_params = {"q": truncated_query, "query_by": query_by}

        results = self.client.collections[collection].documents.search(search_params)
        return [hit["document"] for hit in results["hits"]]

    def full_text_search_by_db_connection_id(
        self, collection: str, db_connection_id: str, query: str, columns: list
    ) -> list:
        self.ensure_collection_exists(collection)
        query_by = ",".join(columns)

        # Truncate query to avoid Typesense 4000 char limit
        truncated_query = self._truncate_query(query)

        search_params = {
            "q": truncated_query,
            "query_by": query_by,
            "filter_by": f"db_connection_id:={db_connection_id}",
        }

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
        self.ensure_collection_exists(collection)

        # Truncate query to avoid Typesense 4000 char limit
        truncated_query = self._truncate_query(query)

        search_requests = {
            "searches": [
                {
                    "collection": collection,
                    "q": truncated_query,
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

        retrieved_queries = query_by.split(',')
        retrieved_queries = [query.strip() for query in retrieved_queries]

        if results:
            if results["results"][0]["found"] > 0:
                hits = results["results"][0]["hits"]

                # Deduplicate by query_by
                unique_hits = {}
                for hit in hits:
                    document = hit['document']
                    key_parts = []

                    for query_field in retrieved_queries:
                        value = document.get(query_field, "")
                        key_parts.append(str(value).lower())

                    deduplication_key = ", ".join(key_parts)
                    if deduplication_key not in unique_hits:
                        unique_hits[deduplication_key] = hit

                # Convert dictionary values back to a list
                hits = list(unique_hits.values())

                # Sort results by vector_distance asc
                sorted_hits = sorted(
                    hits,
                    key=lambda x: x["vector_distance"],
                    reverse=False,
                )
                # Take top N results
                sorted_hits = sorted_hits[:limit]

                # Remapping vector_distance between 0 and 1. Higher is more similar
                return [
                    {**hit["document"], "score": 1 - (hit["vector_distance"] / 2)}
                    for hit in sorted_hits
                ]

        return None

    def delete_by_id(self, collection: str, id: str) -> list[dict]:
        self.ensure_collection_exists(collection)
        deleted = self.client.collections[collection].documents[id].delete()

        return deleted

    def delete_by_filter(self, collection: str, filter: dict) -> int:
        """Delete all documents matching a filter.

        Args:
            collection: Collection name.
            filter: Filter dict with field:value pairs.

        Returns:
            Number of deleted documents.
        """
        self.ensure_collection_exists(collection)

        filter_by = " && ".join(
            [f"{k}:={self._escape_filter_value(v)}" for k, v in filter.items()]
        )

        result = self.client.collections[collection].documents.delete(
            {"filter_by": filter_by}
        )

        return result.get("num_deleted", 0)

    def bulk_update(self, collection: str, documents: list[dict]) -> int:
        """Bulk update documents.

        Args:
            collection: Collection name.
            documents: List of document dicts with 'id' field.

        Returns:
            Number of updated documents.
        """
        self.ensure_collection_exists(collection)

        count = 0
        for doc in documents:
            if "id" in doc:
                doc_id = doc["id"]
                update_data = {k: v for k, v in doc.items() if k != "id"}
                self.client.collections[collection].documents[doc_id].update(
                    update_data
                )
                count += 1
        return count

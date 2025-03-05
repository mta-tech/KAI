from app.data.db.storage import Storage
from app.modules.context_store.models import ContextStore
from difflib import SequenceMatcher

DB_COLLECTION = "context_stores"


class ContextStoreRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, context_store: ContextStore) -> ContextStore:
        context_store_dict = context_store.model_dump(exclude={"id"})
        context_store.id = str(
            self.storage.insert_one(DB_COLLECTION, context_store_dict)
        )
        return context_store

    def find_by(
        self, filter: dict, page: int = 0, limit: int = 0
    ) -> list[ContextStore]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(ContextStore(**row))
        return result

    def find_by_prompt(
        self, db_connection_id: str, prompt_text: str
    ) -> ContextStore | None:
        row = self.storage.find_exactly_one(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id, "prompt_text": prompt_text},
        )
        if not row:
            return None
        return ContextStore(**row)

    def find_by_id(self, id: str) -> ContextStore | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return ContextStore(**row)

    def find_all(self) -> list[ContextStore]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = [ContextStore(**row) for row in rows]
        return result

    def find_by_relevance(
        self,
        db_connection_id: str,
        prompt_text: str,
        prompt_embedding: list[float],
        limit: int = 3,
        alpha: float = 1.0,
    ) -> list | None:
        rows = self.storage.hybrid_search(
            collection=DB_COLLECTION,
            query=prompt_text,
            query_by="prompt_text",
            vector_query=f"prompt_embedding:({prompt_embedding}, alpha:{alpha})",
            exclude_fields="prompt_embedding",
            filter_by=f"db_connection_id:={db_connection_id}",
            limit=limit,
        )

        result = []
        if rows:
            for row in rows:
                result.append(
                    {
                        "prompt_text": row["prompt_text"],
                        "sql": row["sql"],
                        "score": row["score"],
                    }
                )
        return result

    def find_by_prompt_ner(
        self, db_connection_id: str, prompt_text_ner: str, filter_by: dict = None
    ) -> list | None:
        self.storage.ensure_collection_exists(DB_COLLECTION)

        filter_conditions = [f"db_connection_id:={db_connection_id}"]
        if filter_by:
            for key, val in filter_by.items():
                filter_conditions.append(f"{key}:={val}")

        filter_conditions = " && ".join(filter_conditions)

        search_requests = {
            "searches": [
                {
                    "collection": DB_COLLECTION,
                    "q": prompt_text_ner,
                    "query_by": "prompt_text_ner",
                    "exclude_fields": "prompt_embedding",
                }
            ]
        }

        common_search_params = {}
        if filter_by:
            common_search_params["filter_by"] = filter_conditions

        results = self.storage.client.multi_search.perform(
            search_requests, common_search_params
        )

        result = []
        if results:
            if results["results"][0]["found"] > 0:
                hits = results["results"][0]["hits"]
                for row in hits:
                    score = SequenceMatcher(
                        None, row["document"]["prompt_text_ner"], prompt_text_ner
                    ).ratio()
                    print("Score similarity:", score)
                    if score >= 0.95:
                        print("Cached HIT!")
                        result.append(
                            {
                                "prompt_text": row["document"]["prompt_text"],
                                "prompt_text_ner": row["document"]["prompt_text_ner"],
                                "sql": row["document"]["sql"],
                                "score": score,
                            }
                        )

                result = sorted(
                    result,
                    key=lambda x: x["score"],
                    reverse=True,
                )
            return result
        return None

    def delete_by_id(self, id: str) -> bool:
        deleted_count = self.storage.delete_by_id(DB_COLLECTION, id)
        return deleted_count > 0

    def update(self, context_store: ContextStore) -> ContextStore:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": context_store.id},
            context_store.model_dump(exclude={"id"}),
        )
        return context_store

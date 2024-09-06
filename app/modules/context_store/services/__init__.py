from fastapi import HTTPException

from app.api.requests import (  # , UpdateContextStoreRequest
    ContextStoreRequest,
    UpdateContextStoreRequest,
)
from app.modules.context_store.models import ContextStore
from app.modules.context_store.repositories import ContextStoreRepository

# from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository


class ContextStoreService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = ContextStoreRepository(self.storage)

    def create_context_store(
        self, context_store_request: ContextStoreRequest
    ) -> ContextStore:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            context_store_request.db_connection_id
        )
        if not db_connection:
            raise HTTPException(
                f"Database connection {context_store_request.db_connection_id} not found"
            )

        context_store = ContextStore(
            db_connection_id=context_store_request.db_connection_id,
            prompt=context_store_request.prompt,
            sql=context_store_request.sql,
            metadata=context_store_request.metadata,
        )
        return self.repository.insert(context_store)

    def get_context_store(self, context_store_id) -> ContextStore:
        context_store = self.repository.find_by_id(context_store_id)
        if not context_store:
            raise HTTPException(f"Prompt {context_store_id} not found")
        return context_store

    def get_context_stores(self, db_connection_id) -> list[ContextStore]:
        filter = {"db_connection_id": db_connection_id}
        return self.repository.find_by(filter)

    def update_context_store(
        self, context_store_id, update_request: UpdateContextStoreRequest
    ) -> ContextStore:
        context_store = self.repository.find_by_id(context_store_id)
        if not context_store:
            raise HTTPException(f"ContextStore {context_store_id} not found")

        for key, value in update_request.model_dump(exclude_unset=True).items():
            setattr(context_store, key, value)

        self.repository.update(context_store_id, context_store)
        return context_store

    def delete_context_store(self, context_store_id) -> bool:
        context_store = self.repository.find_by_id(context_store_id)
        if not context_store:
            raise HTTPException(f"Prompt {context_store_id} not found")

        is_deleted = self.repository.delete_by_id(context_store_id)

        if not is_deleted:
            raise HTTPException(f"Failed to delete context_store {context_store_id}")

        return True

    def full_text_search(self, db_connection_id, prompt) -> ContextStore:
        return self.repository.find_by_prompt(db_connection_id, prompt)

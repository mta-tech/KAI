
from app.api.requests import ContextStoreRequest #, UpdateContextStoreRequest
# from app.modules.database_connection.models import DatabaseConnection
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.context_store.models import ContextStore
from app.modules.context_store.repositories import ContextStoreRepository


class ContextStoreService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = ContextStoreRepository(self.storage)

    def create_context_store(self, context_store_request: ContextStoreRequest) -> ContextStore:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            context_store_request.db_connection_id
        )
        if not db_connection:
            raise Exception(
                f"Database connection {context_store_request.db_connection_id} not found"
            )

        # if not db_connection.schemas and prompt_request.schemas:
        #     raise Exception(
        #         "Schema not supported for this db",
        #         description=f"The {db_connection.dialect} dialect doesn't support schemas",
        #     )
        get_parameterized = self.check_parameterized(context_store_request.prompt_text)

        context_store = ContextStore(
            db_connection_id=context_store_request.db_connection_id,
            prompt_text=context_store_request.prompt_text,
            prompt_text_embedding= self.get_embedding(context_store_request.prompt_text), 
            sql=context_store_request.sql,
            is_parameterized=get_parameterized[0],
            parameterized_entity=get_parameterized[1],
            metadata=context_store_request.metadata,
        )
        return self.repository.insert(context_store)

    def get_context_store(self, context_store_id) -> ContextStore:
        context_store = self.repository.find_by_id(context_store_id)
        if not context_store:
            raise Exception(f"Prompt {context_store_id} not found")
        return context_store

    def get_context_stores(self, db_connection_id) -> list[ContextStore]:
        filter = {"db_connection_id": db_connection_id}
        return self.repository.find_by(filter)

    # def update_context_store(
    #     self, context_store_id, update_request: UpdateContextStoreRequest
    # ) -> ContextStore:
    #     context_store = self.repository.find_by_id(context_store_id)
    #     if not context_store:
    #         raise Exception(f"ContextStore {context_store_id} not found")
        
    #     if update_request.prompt_text is not None:
    #         context_store.prompt_text = update_request.prompt_text
    #         context_store.prompt_text_embedding = self.get_embedding(update_request.prompt_text)
    #     if update_request.sql is not None:
    #         context_store.sql = update_request.sql
    #     if update_request.is_parameterized is not None:
    #         context_store.is_parameterized = update_request.is_parameterized
    #     if update_request.metadata is not None:
    #         context_store.metadata = update_request.metadata

    #     return self.repository.update(context_store)

    def delete_context_store(self, context_store_id) -> bool:
        context_store = self.repository.find_by_id(context_store_id)
        if not context_store:
            raise Exception(f"Prompt {context_store_id} not found")
        
        is_deleted = self.repository.delete_by_id(context_store_id)

        if not is_deleted:
            raise Exception(f"Failed to delete context_store {context_store_id}")
        
        return True



# TODO Link to embedding module, link to NER module
    def get_embedding(self, text) -> list[float] | None:
        print(f'Run get_embedding on: {text}')
        return None
    
    def check_parameterized(self, text) -> tuple:
        ans = (False, None)
        print(f"Check NER parameter for: {text}")
        return ans
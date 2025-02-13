import logging
import os
from fastapi import HTTPException
from sql_metadata import Parser
from dotenv import load_dotenv

from app.api.requests import (
    ContextStoreRequest,
    UpdateContextStoreRequest,
)
from app.modules.context_store.models import ContextStore
from app.modules.context_store.repositories import ContextStoreRepository
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.prompt.models import Prompt
from app.utils.model.embedding_model import EmbeddingModel
from app.utils.model.chat_model import ChatModel
from app.utils.sql_database.sql_utils import extract_the_schemas_from_sql
from app.utils.prompts_ner.prompts_ner import (
    get_ner_labels,
    # request_ner_service,
    request_ner_llm,
    get_labels_entities,
    # get_prompt_text_ner
    replace_entities_with_labels
)

load_dotenv()
logger = logging.getLogger(__name__)


class ContextStoreService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = ContextStoreRepository(self.storage)

    def create_context_store(
        self, context_store_request: ContextStoreRequest
    ) -> ContextStore:
        try:
            Parser(context_store_request.sql).tables  # noqa: B018
        except Exception as e:
            raise HTTPException(
                404,
                f"SQL {context_store_request.sql} is malformed. Please check the syntax.",
            ) from e

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            context_store_request.db_connection_id
        )
        if not db_connection:
            raise HTTPException(
                f"Database connection {context_store_request.db_connection_id} not found"
            )

        if db_connection.schemas:
            schema_not_found = True
            used_schemas = extract_the_schemas_from_sql(context_store_request.sql)
            for schema in db_connection.schemas:
                if schema in used_schemas:
                    schema_not_found = False
                    break
            if schema_not_found:
                raise HTTPException(
                    404,
                    f"SQL {context_store_request.sql} does not contain any of the schemas {db_connection.schemas}",
                )

        # Get Embedding Vector from Prompt, used in SQL Generation as Few Show Examples
        embedding_model = EmbeddingModel().get_model()
        prompt_embedding = embedding_model.embed_query(
            context_store_request.prompt_text
        )
        prompt_text_ner = context_store_request.prompt_text
        labels_entities = {
            'entities':[],
            'labels':[]
        }
        try:
            llm_model = ChatModel().get_model(
                        database_connection=None,
                        model_family=os.getenv("CHAT_FAMILY"),
                        model_name=os.getenv("CHAT_MODEL"),
                        api_base=None,
                        temperature=0,
                        max_retries=2
                    )
            labels = get_ner_labels(context_store_request.prompt_text)
            # labels_entities_ner = request_ner_service(context_store_request.prompt_text, labels)
            labels_entities_ner = request_ner_llm(llm_model, context_store_request.prompt_text, labels)
            # prompt_text_ner = get_prompt_text_ner(context_store_request.prompt_text, labels_entities_ner)
            if labels_entities_ner[0]:
                prompt_text_ner = replace_entities_with_labels(context_store_request.prompt_text, labels_entities_ner)
                labels_entities = get_labels_entities(labels_entities_ner)
        except:
            pass


        context_store = ContextStore(
            db_connection_id=context_store_request.db_connection_id,
            prompt_text=context_store_request.prompt_text,
            prompt_text_ner=prompt_text_ner,
            entities=labels_entities['entities'],
            labels=labels_entities['labels'],
            prompt_embedding=prompt_embedding,
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

    def retrieve_exact_prompt(self, db_connection_id, prompt) -> ContextStore:
        return self.repository.find_by_prompt(db_connection_id, prompt)

    def retrieve_exact_prompt_ner(self, db_connection_id, prompt_text_ner, filter_by) -> ContextStore:
        return self.repository.find_by_prompt_ner(
                db_connection_id,
                prompt_text_ner,
                filter_by
            )

    def retrieve_context_for_question(self, prompt: Prompt) -> list[dict]:
        logger.info(f"Getting context for {prompt.text}")

        embedding_model = EmbeddingModel().get_model()
        prompt_embedding = embedding_model.embed_query(prompt.text)
        relevant_context = self.repository.find_by_relevance(
            prompt.db_connection_id, prompt.text, prompt_embedding
        )

        return relevant_context

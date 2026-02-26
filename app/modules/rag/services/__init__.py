from fastapi import HTTPException
from app.api.requests import TextRequest, EmbeddingRequest

# from app.modules.database_connection.models import DatabaseConnection
# from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.rag.models import DocumentStore, RetrieveKnowledge
from app.modules.rag.repositories import DocumentRepository

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.vector_stores.typesense import TypesenseVectorStore
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.core.ingestion import IngestionPipeline
# Use local adapter instead of broken llama-index-llms-langchain
from app.utils.llm_adapters import LangChainLLM
from langchain_community.callbacks import get_openai_callback

# from llama_index.core import VectorStoreIndex
# from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import VectorStoreQuery
from typing import Optional
from typing import Any, List
from dotenv import load_dotenv
import os

from app.data.db.storage import Storage
from app.utils.model.chat_model import ChatModel
from app.utils.model.embedding_model import EmbeddingModel

load_dotenv()


class DocumentService:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.repository = DocumentRepository(self.storage)

    def create_document(self, embedding_request: TextRequest) -> DocumentStore:
        document = DocumentStore(
            title=embedding_request.title,
            content_type="text",
            document_size=len(embedding_request.text_content),
            text_content=embedding_request.text_content,
            metadata=embedding_request.metadata,
        )
        return self.repository.insert(document)

    def get_document(self, document_id) -> DocumentStore:
        document = self.repository.find_by_id(document_id)
        if not document:
            raise HTTPException(f"Prompt {document_id} not found")
        return document

    def get_documents(self) -> list[DocumentStore]:
        return self.repository.find_all()

    def delete_document(self, document_id) -> bool:
        document = self.repository.find_by_id(document_id)
        if not document:
            raise HTTPException(f"Prompt {document_id} not found")

        is_deleted = self.repository.delete_by_id(document_id)

        if not is_deleted:
            raise HTTPException(f"Failed to delete document {document_id}")

        return True


# TODO Embedding Service should use by Settings and Embedding Factory not initiate by itself
class EmbeddingService:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.repository = DocumentRepository(self.storage)
        self.embedding_model = LangchainEmbedding(EmbeddingModel().get_model())
        self.collection_target = "knowledge-stores"
        self.vector_store = TypesenseVectorStore(
            client=self.storage.client, collection_name=self.collection_target
        )

        self.query_engine = self.create_query_engine()

    def create_embedding(self, embedding_request: EmbeddingRequest) -> DocumentStore:
        document = self.create_llama_document(embedding_request)
        pipeline = self.create_ingestion_pipeline(self.vector_store)
        pipeline.run(documents=[document])
        return True

    def create_ingestion_pipeline(self, vector_store: TypesenseVectorStore):
        return IngestionPipeline(
            transformations=[
                TokenTextSplitter(chunk_size=512, chunk_overlap=10),
                # TitleExtractor(llm=llm),
                self.embedding_model,
            ],
            vector_store=vector_store,
        )

    def create_llama_document(self, embedding_request: EmbeddingRequest) -> Document:
        text = embedding_request.text_content
        # metadata = embedding_request.metadata
        title = embedding_request.title
        document = Document(text=text)
        document.metadata["title"] = title
        document.id_ = embedding_request.document_id
        return document

    def create_query_engine(
        self, top_k: int = 4, cutoff: float = 0.80
    ) -> RetrieverQueryEngine:
        retriever = VectorDBRetriever(
            self.vector_store,
            embed_model=self.embedding_model,
            query_mode="default",
            similarity_top_k=top_k,
        )
        # cutoff is not used for now
        llm_model = LangChainLLM(llm=ChatModel().get_model(
                        database_connection=None,
                        model_family=os.getenv("CHAT_FAMILY"),
                        model_name=os.getenv("CHAT_MODEL"),
                        max_retries=2
                    ))
        query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm_model)
        return query_engine

    def query(self, query_request: str) -> RetrieveKnowledge:
        with get_openai_callback() as cb:
            response = self.query_engine.query(query_request)
        
        return_dict = {
            "final_answer": str(response),
            "input_tokens_used": cb.prompt_tokens,
            "output_tokens_used": cb.completion_tokens
        }

        return RetrieveKnowledge(**return_dict)


class VectorDBRetriever(BaseRetriever):
    """Retriever over any vector store."""

    def __init__(
        self,
        vector_store: Any,
        embed_model: Any,
        query_mode: str = "default",
        similarity_top_k: int = 2,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        query_embedding = self._embed_model.get_query_embedding(query_bundle.query_str)
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = self._vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores

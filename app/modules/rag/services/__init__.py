
from fastapi import HTTPException
from app.api.requests import TextRequest, EmbeddingRequest
# from app.modules.database_connection.models import DatabaseConnection
# from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.rag.models import DocumentStore
from app.modules.rag.repositories import DocumentRepository

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.vector_stores.typesense import TypesenseVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.llms.openai import OpenAI
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
from typesense import Client
from dotenv import load_dotenv
import os

load_dotenv()


class DocumentService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = DocumentRepository(self.storage)

    def create_document(self, embedding_request: TextRequest) -> DocumentStore:
        document = DocumentStore(
            title = embedding_request.title,
            content_type = "text",
            document_size = len(embedding_request.text_content),
            text_content = embedding_request.text_content,
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

class EmbeddingService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = DocumentRepository(self.storage)
        self.typesense_api_key = os.getenv("TYPESENSE_API_KEY")
        self.typesense_host = os.getenv("TYPESENSE_HOST")
        self.typesense_port = os.getenv("TYPESENSE_PORT")
        self.typesense_protocol = os.getenv("TYPESENSE_PROTOCOL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.chat_model = os.getenv("CHAT_MODEL")
        self.llm = OpenAI(api_key=self.openai_api_key, model=self.chat_model)
        self.embedding_model = OpenAIEmbedding(api_key=self.openai_api_key)
        self.collection_target = "knowledge-stores"
        self.typesense_client = self.create_typesense_client()
        self.vector_store = TypesenseVectorStore(client=self.typesense_client,
                                            collection_name=self.collection_target)

        self.query_engine = self.create_query_engine()


    def create_embedding(self, embedding_request: EmbeddingRequest) -> DocumentStore:
        document = self.create_llama_document(embedding_request)
        pipeline = self.create_ingestion_pipeline(self.vector_store)
        pipeline.run(documents=[document])
        return True
    
    def create_typesense_client(self) -> Client:
        typesense_client = Client(
            {
                "api_key": self.typesense_api_key,
                "nodes": [{"host": self.typesense_host, 
                           "port": self.typesense_port, 
                           "protocol": self.typesense_protocol}],
                           "connection_timeout_seconds": 2,
            }
        )
        return typesense_client

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
        document.metadata['title'] = title
        document.id_ = embedding_request.document_id
        return document

    def create_query_engine(self, top_k: int = 4, cutoff: float = 0.80) -> RetrieverQueryEngine:
        retriever = VectorDBRetriever(self.vector_store, 
                                      embed_model=self.embedding_model, 
                                      query_mode="default", 
                                      similarity_top_k=top_k)
        #cutoff is not used for now
        query_engine = RetrieverQueryEngine.from_args(retriever, llm=self.llm)
        return query_engine
    
    def query(self, query_request: str) -> str:
        response = self.query_engine.query(query_request)
        return str(response)

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
        query_embedding = self._embed_model.get_query_embedding(
            query_bundle.query_str
        )
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
    

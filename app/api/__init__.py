from io import BytesIO

import fastapi
import PyPDF2
from fastapi import BackgroundTasks, File, HTTPException, UploadFile
# from fastapi.responses import JSONResponse

from app.api.requests import (
    AliasRequest,
    BusinessGlossaryRequest,
    ContextStoreRequest,
    GetContextStoreByNameRequest,
    SemanticContextStoreRequest,
    DatabaseConnectionRequest,
    InstructionRequest,
    NLGenerationRequest,
    NLGenerationsSQLGenerationRequest,
    PromptRequest,
    PromptSQLGenerationNLGenerationRequest,
    PromptSQLGenerationRequest,
    ScannerRequest,
    SQLGenerationRequest,
    TableDescriptionRequest,
    UpdateAliasRequest,
    UpdateBusinessGlossaryRequest,
    UpdateInstructionRequest,
    UpdateMetadataRequest,
    TextRequest,
    EmbeddingRequest,
    SyntheticQuestionRequest,
)
from app.api.responses import (
    AliasResponse,
    BusinessGlossaryResponse,
    ContextStoreResponse,
    DatabaseConnectionResponse,
    InstructionResponse,
    NLGenerationResponse,
    PromptResponse,
    SQLGenerationResponse,
    TableDescriptionResponse,
    DocumentResponse,
    RetrieveKnowledgeResponse,
    SyntheticQuestionResponse,
)
from app.data.db.storage import Storage
from app.modules.alias.services import AliasService
from app.modules.business_glossary.services import BusinessGlossaryService
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.instruction.services import InstructionService
from app.modules.nl_generation.services import NLGenerationService
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.services import SQLGenerationService
from app.modules.table_description.services import TableDescriptionService
from app.modules.rag.services import DocumentService, EmbeddingService
from app.modules.synthetic_questions.services import SyntheticQuestionService
from app.utils.sql_database.scanner import SqlAlchemyScanner


class API:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.router = fastapi.APIRouter()
        self.database_connection_service = DatabaseConnectionService(
            scanner=SqlAlchemyScanner(), storage=self.storage
        )
        self.table_description_service = TableDescriptionService(self.storage)
        self.prompt_service = PromptService(self.storage)
        self.business_glossary_service = BusinessGlossaryService(self.storage)
        self.sql_generation_service = SQLGenerationService(self.storage)
        self.instruction_service = InstructionService(self.storage)
        self.context_store_service = ContextStoreService(self.storage)
        self.nl_generation_service = NLGenerationService(self.storage)
        self.document_service = DocumentService(self.storage)
        self.embedding_service = EmbeddingService(self.storage)
        self.synthetic_question_service = SyntheticQuestionService(self.storage)
        self.alias_service = AliasService(self.storage)

        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/api/v1/database-connections",
            self.create_database_connection,
            methods=["POST"],
            status_code=201,
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections",
            self.list_database_connections,
            methods=["GET"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections/{db_connection_id}",
            self.update_database_connection,
            methods=["PUT"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections/{db_connection_id}",
            self.delete_database_connection,
            methods=["DELETE"],
            tags=["Database Connections"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/sync-schemas",
            self.scan_db,
            methods=["POST"],
            status_code=201,
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/refresh",
            self.refresh_table_description,
            methods=["POST"],
            status_code=201,
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.update_table_description,
            methods=["PUT"],
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions",
            self.list_table_descriptions,
            methods=["GET"],
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.get_table_description,
            methods=["GET"],
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.delete_table_description,
            methods=["DELETE"],
            tags=["Table Descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions",
            self.create_instruction,
            methods=["POST"],
            status_code=201,
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions",
            self.get_instructions,
            methods=["GET"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions/{instruction_id}",
            self.get_instruction,
            methods=["GET"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions/{instruction_id}",
            self.update_instruction,
            methods=["PUT"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions/{instruction_id}",
            self.delete_instruction,
            methods=["DELETE"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/context-stores",
            self.create_context_store,
            methods=["POST"],
            status_code=201,
            tags=["Context Stores"],
        )

        self.router.add_api_route(
            "/api/v1/context-stores",
            self.get_context_stores,
            methods=["GET"],
            tags=["Context Stores"],
        )

        self.router.add_api_route(
            "/api/v1/context-stores/{context_store_id}",
            self.get_context_store,
            methods=["GET"],
            tags=["Context Stores"],
        )

        self.router.add_api_route(
            "/api/v1/context-stores/get-by-prompt",
            self.get_context_store_by_prompt,
            methods=["POST"],
            tags=["Context Stores"],
        )
        self.router.add_api_route(
            "/api/v1/context-stores/semantic-search",
            self.get_semantic_context_stores,
            methods=["POST"],
            status_code=201,
            tags=["Context Stores"],
        )

        self.router.add_api_route(
            "/api/v1/context-stores/{context_store_id}",
            self.delete_context_store,
            methods=["DELETE"],
            tags=["Context Stores"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries",
            self.create_business_glossary,
            methods=["POST"],
            status_code=201,
            tags=["Business Glossaries"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries",
            self.get_business_glossaries,
            methods=["GET"],
            tags=["Business Glossaries"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries/{business_glossary_id}",
            self.get_business_glossary,
            methods=["GET"],
            tags=["Business Glossaries"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries/{business_glossary_id}",
            self.update_business_glossary,
            methods=["PUT"],
            tags=["Business Glossaries"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries/{business_glossary_id}",
            self.delete_business_glossary,
            methods=["DELETE"],
            tags=["Business Glossaries"],
        )

        self.router.add_api_route(
            "/api/v1/prompts",
            self.create_prompt,
            methods=["POST"],
            status_code=201,
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}",
            self.get_prompt,
            methods=["GET"],
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts",
            self.get_prompts,
            methods=["GET"],
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}",
            self.update_prompt,
            methods=["PUT"],
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}/sql-generations",
            self.create_sql_generation,
            methods=["POST"],
            status_code=201,
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/sql-generations",
            self.create_prompt_and_sql_generation,
            methods=["POST"],
            status_code=201,
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations",
            self.get_sql_generations,
            methods=["GET"],
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}",
            self.get_sql_generation,
            methods=["GET"],
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}",
            self.update_sql_generation,
            methods=["PUT"],
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/execute",
            self.execute_sql_query,
            methods=["GET"],
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/execute-store",
            self.create_csv_execute_sql_query,
            methods=["GET"],
            tags=["SQL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/nl-generations",
            self.create_nl_generation,
            methods=["POST"],
            status_code=201,
            tags=["NL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}/sql-generations/nl-generations",
            self.create_sql_and_nl_generation,
            methods=["POST"],
            status_code=201,
            tags=["NL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/sql-generations/nl-generations",
            self.create_prompt_sql_and_nl_generation,
            methods=["POST"],
            status_code=201,
            tags=["NL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/nl-generations",
            self.get_nl_generations,
            methods=["GET"],
            tags=["NL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/nl-generations/{nl_generation_id}",
            self.get_nl_generation,
            methods=["GET"],
            tags=["NL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/nl-generations/{nl_generation_id}",
            self.update_nl_generation,
            methods=["PUT"],
            tags=["NL Generations"],
        )

        self.router.add_api_route(
            "/api/v1/rags/upload-document",
            self.upload_document,
            methods=["POST"],
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/rags/create-document",
            self.create_document,
            methods=["POST"],
            status_code=201,
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/rags/documents",
            self.get_documents,
            methods=["GET"],
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/rags/documents/{document_id}",
            self.get_document,
            methods=["GET"],
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/rags/documents/{document_id}",
            self.delete_document,
            methods=["DELETE"],
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/rags/embeddings/",
            self.embed_document,
            methods=["POST"],
            status_code=201,
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/rags/embeddings/",
            self.retrieve_knowledge,
            methods=["GET"],
            tags=["RAGs"],
        )

        self.router.add_api_route(
            "/api/v1/aliases",
            self.create_alias,
            methods=["POST"],
            status_code=201,
            tags=["Aliases"],
        )

        self.router.add_api_route(
            "/api/v1/aliases",
            self.get_aliases,
            methods=["GET"],
            tags=["Aliases"],
        )

        self.router.add_api_route(
            "/api/v1/aliases/get-by-name",
            self.get_alias_by_name,
            methods=["GET"],
            tags=["Aliases"],
        )

        self.router.add_api_route(
            "/api/v1/aliases/{alias_id}",
            self.get_alias,
            methods=["GET"],
            tags=["Aliases"],
        )

        self.router.add_api_route(
            "/api/v1/aliases/{alias_id}",
            self.update_alias,
            methods=["PUT"],
            tags=["Aliases"],
        )

        self.router.add_api_route(
            "/api/v1/aliases/{alias_id}",
            self.delete_alias,
            methods=["DELETE"],
            tags=["Aliases"],
        )

        self.router.add_api_route(
            "/api/v1/synthetic-questions",
            self.generate_synthetic_questions,
            methods=["POST"],
            tags=["Question Generation"],
        )

    def get_router(self) -> fastapi.APIRouter:
        return self.router

    def create_database_connection(
        self, request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        db_connection = self.database_connection_service.create_database_connection(
            request
        )
        return DatabaseConnectionResponse(**db_connection.model_dump())

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        db_connections = self.database_connection_service.list_database_connections()
        return [
            DatabaseConnectionResponse(**db_connection.model_dump())
            for db_connection in db_connections
        ]

    def update_database_connection(
        self,
        db_connection_id: str,
        request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        db_connection = self.database_connection_service.update_database_connection(
            db_connection_id, request
        )
        return DatabaseConnectionResponse(**db_connection.model_dump())

    def delete_database_connection(
        self,
        db_connection_id: str,
    ) -> DatabaseConnectionResponse:
        db_connection = self.database_connection_service.delete_database_connection(
            db_connection_id
        )
        return DatabaseConnectionResponse(**db_connection.model_dump())

    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> list[TableDescriptionResponse]:
        table_descriptions = self.table_description_service.scan_db(
            scanner_request, background_tasks
        )
        return [
            TableDescriptionResponse(**table_description.model_dump())
            for table_description in table_descriptions
        ]

    def refresh_table_description(
        self, database_connection_id: str
    ) -> list[TableDescriptionResponse]:
        table_descriptions = self.table_description_service.refresh_table_description(
            database_connection_id
        )
        return [
            TableDescriptionResponse(**table_description.model_dump())
            for table_description in table_descriptions
        ]

    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableDescriptionResponse:
        """Add descriptions for tables and columns"""
        table_description = self.table_description_service.update_table_description(
            table_description_id, table_description_request
        )
        return TableDescriptionResponse(**table_description.model_dump())

    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescriptionResponse]:
        """List table descriptions"""
        table_descriptions = self.table_description_service.list_table_descriptions(
            db_connection_id, table_name
        )
        return [
            TableDescriptionResponse(**table_description.model_dump())
            for table_description in table_descriptions
        ]

    def get_table_description(
        self, table_description_id: str
    ) -> TableDescriptionResponse:
        """Get description"""
        table_description = self.table_description_service.get_table_description(
            table_description_id
        )
        return TableDescriptionResponse(**table_description.model_dump())

    def delete_table_description(
        self, table_description_id: str
    ) -> TableDescriptionResponse:
        """Delete description"""
        table_description = self.table_description_service.delete_table_description(
            table_description_id
        )
        return TableDescriptionResponse(**table_description.model_dump())

    def create_prompt(self, prompt_request: PromptRequest) -> PromptResponse:
        prompt = self.prompt_service.create_prompt(prompt_request)
        return PromptResponse(**prompt.model_dump())

    def get_prompts(self, db_connection_id: str) -> list[PromptResponse]:
        prompts = self.prompt_service.get_prompts(db_connection_id)
        return [PromptResponse(**prompt.model_dump()) for prompt in prompts]

    def get_prompt(self, prompt_id: str) -> PromptResponse:
        prompt = self.prompt_service.get_prompt(prompt_id)
        return PromptResponse(**prompt.model_dump())

    def update_prompt(
        self, prompt_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> PromptResponse:
        prompt = self.prompt_service.update_prompt(prompt_id, update_metadata_request)
        return PromptResponse(**prompt.model_dump())

    def create_instruction(
        self, instruction_request: InstructionRequest
    ) -> InstructionResponse:
        instruction = self.instruction_service.create_instruction(instruction_request)
        return InstructionResponse(**instruction.model_dump())

    def get_instructions(self, db_connection_id: str) -> list[InstructionResponse]:
        instructions = self.instruction_service.get_instructions(db_connection_id)
        return [
            InstructionResponse(**instruction.model_dump())
            for instruction in instructions
        ]

    def get_instruction(self, instruction_id: str) -> InstructionResponse:
        instruction = self.instruction_service.get_instruction(instruction_id)
        return InstructionResponse(**instruction.model_dump())

    def update_instruction(
        self, instruction_id: str, update_instruction_request: UpdateInstructionRequest
    ) -> InstructionResponse:
        instruction = self.instruction_service.update_instruction(
            instruction_id, update_instruction_request
        )
        return InstructionResponse(**instruction.model_dump())

    def delete_instruction(self, instruction_id: str) -> dict:
        try:
            is_deleted = self.instruction_service.delete_instruction(instruction_id)
            if is_deleted:
                return {"message": f"Instruction {instruction_id} successfully deleted"}
        except Exception as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=500, detail=str(e))

    def create_context_store(
        self, context_store_request: ContextStoreRequest
    ) -> ContextStoreResponse:
        context_store = self.context_store_service.create_context_store(
            context_store_request
        )
        return ContextStoreResponse(**context_store.model_dump())

    def get_context_stores(self, db_connection_id: str) -> list[ContextStoreResponse]:
        context_stores = self.context_store_service.get_context_stores(db_connection_id)
        return [
            ContextStoreResponse(**context_store.model_dump())
            for context_store in context_stores
        ]

    def get_context_store(self, context_store_id: str) -> ContextStoreResponse:
        context_store = self.context_store_service.get_context_store(context_store_id)
        return ContextStoreResponse(**context_store.model_dump())

    def get_context_store_by_prompt(
        self, context_store_request: GetContextStoreByNameRequest
    ) -> list[ContextStoreResponse]:
        context_stores = self.context_store_service.get_context_stores_by_prompt(
            context_store_request.db_connection_id, context_store_request.prompt_text
        )
        return [
            ContextStoreResponse(**context_store.model_dump())
            for context_store in context_stores
        ]

    def get_semantic_context_stores(
        self, context_store_request: SemanticContextStoreRequest
    ) -> list[dict]:
        semantic_context_stores = (
            self.context_store_service.get_semantic_context_stores(
                context_store_request.db_connection_id,
                context_store_request.prompt_text,
                context_store_request.top_k,
            )
        )

        return [context_store for context_store in semantic_context_stores]

    def delete_context_store(self, context_store_id: str) -> dict:
        try:
            is_deleted = self.context_store_service.delete_context_store(
                context_store_id
            )
            if is_deleted:
                return {"message": f"Context {context_store_id} successfully deleted"}
        except Exception as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=500, detail=str(e))

    def create_business_glossary(
        self, db_connection_id: str, business_glossary_request: BusinessGlossaryRequest
    ) -> BusinessGlossaryResponse:
        business_glossary = self.business_glossary_service.create_business_glossary(
            db_connection_id, business_glossary_request
        )
        return BusinessGlossaryResponse(**business_glossary.model_dump())

    def get_business_glossaries(
        self, db_connection_id: str
    ) -> list[BusinessGlossaryResponse]:
        business_glossaries = self.business_glossary_service.get_business_glossaries(
            db_connection_id
        )
        return [
            BusinessGlossaryResponse(**business_glossary.model_dump())
            for business_glossary in business_glossaries
        ]

    def get_business_glossary(
        self, business_glossary_id: str
    ) -> BusinessGlossaryResponse:
        business_glossary = self.business_glossary_service.get_business_glossary(
            business_glossary_id
        )
        return BusinessGlossaryResponse(**business_glossary.model_dump())

    def update_business_glossary(
        self,
        business_glossary_id: str,
        business_glossary_request: UpdateBusinessGlossaryRequest,
    ) -> BusinessGlossaryResponse:
        business_glossary = self.business_glossary_service.update_business_glossary(
            business_glossary_id, business_glossary_request
        )
        return BusinessGlossaryResponse(**business_glossary.model_dump())

    def delete_business_glossary(
        self,
        business_glossary_id: str,
    ) -> dict:
        deleted = self.business_glossary_service.delete_business_glossary(
            business_glossary_id
        )
        return deleted

    def create_sql_generation(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGenerationResponse:
        sql_generation = self.sql_generation_service.create_sql_generation(
            prompt_id, sql_generation_request
        )
        return SQLGenerationResponse(**sql_generation.model_dump())

    def create_prompt_and_sql_generation(
        self, prompt_sql_generation_request: PromptSQLGenerationRequest
    ) -> SQLGenerationResponse:
        sql_generation = self.sql_generation_service.create_prompt_and_sql_generation(
            prompt_sql_generation_request
        )
        return SQLGenerationResponse(**sql_generation.model_dump())

    def get_sql_generations(self, prompt_id: str) -> list[SQLGenerationResponse]:
        sql_generations = self.sql_generation_service.get_sql_generations(prompt_id)
        return [
            SQLGenerationResponse(**sql_generation.model_dump())
            for sql_generation in sql_generations
        ]

    def get_sql_generation(self, sql_generation_id: str) -> SQLGenerationResponse:
        sql_generation = self.sql_generation_service.get_sql_generation(
            sql_generation_id
        )
        return SQLGenerationResponse(**sql_generation.model_dump())

    def update_sql_generation(
        self, sql_generation_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> SQLGenerationResponse:
        sql_generation = self.sql_generation_service.update_sql_generation(
            sql_generation_id, update_metadata_request
        )
        return SQLGenerationResponse(**sql_generation.model_dump())

    def execute_sql_query(self, sql_generation_id: str, max_rows: int = 100) -> list:
        """Executes a SQL query against the database and returns the results"""
        return self.sql_generation_service.execute_sql_query(
            sql_generation_id, max_rows
        )

    def create_csv_execute_sql_query(
        self, sql_generation_id: str, max_rows: int = 100
    ) -> dict:
        return self.sql_generation_service.create_csv_execute_sql_query(
            sql_generation_id, max_rows
        )

    def create_nl_generation(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGenerationResponse:
        nl_generation = self.nl_generation_service.create_nl_generation(
            sql_generation_id, nl_generation_request
        )
        return NLGenerationResponse(**nl_generation.model_dump())

    def create_sql_and_nl_generation(
        self,
        prompt_id: str,
        nl_generation_sql_generation_request: NLGenerationsSQLGenerationRequest,
    ) -> NLGenerationResponse:
        nl_generation = self.nl_generation_service.create_sql_and_nl_generation(
            prompt_id, nl_generation_sql_generation_request
        )
        return NLGenerationResponse(**nl_generation.model_dump())

    def create_prompt_sql_and_nl_generation(
        self, request: PromptSQLGenerationNLGenerationRequest
    ) -> NLGenerationResponse:
        nl_generation = self.nl_generation_service.create_prompt_sql_and_nl_generation(
            request
        )
        return NLGenerationResponse(**nl_generation.model_dump())

    def get_nl_generations(self, sql_generation_id: str) -> list[NLGenerationResponse]:
        nl_generations = self.nl_generation_service.get_nl_generations(
            sql_generation_id
        )
        return [
            NLGenerationResponse(**nl_generation.model_dump())
            for nl_generation in nl_generations
        ]

    def get_nl_generation(self, nl_generation_id: str) -> NLGenerationResponse:
        nl_generation = self.nl_generation_service.get_nl_generation(nl_generation_id)
        return NLGenerationResponse(**nl_generation.model_dump())

    def update_nl_generation(
        self, nl_generation_id: str, metadata_request: UpdateMetadataRequest
    ) -> NLGenerationResponse:
        nl_generation = self.nl_generation_service.update_nl_generation(
            nl_generation_id, metadata_request
        )
        return NLGenerationResponse(**nl_generation.model_dump())

    async def upload_document(self, file: UploadFile = File(...)) -> DocumentResponse:
        try:
            # Read the file content into memory
            content = await file.read()
            text_content = self.pdf_to_text(content)

            text_request = TextRequest(
                title=file.filename,
                content_type=file.content_type,
                document_size=len(content),
                text_content=text_content,
            )

            # Create the document
            document = self.create_document(text_request)

            return document

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def pdf_to_text(self, content: bytes) -> str:
        text = ""
        try:
            # Use BytesIO to treat the content as a file-like object
            pdf_file = BytesIO(content)

            # Create a PDF reader object
            reader = PyPDF2.PdfReader(pdf_file)

            # Extract text from each page
            for page in reader.pages:
                text += page.extract_text() + "\n"

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing PDF: {str(e)}"
            )

        return text

    def embed_document(self, document_id: str) -> dict:
        document = self.document_service.get_document(document_id)
        request = EmbeddingRequest(
            document_id=document_id,
            title=document.title,
            text_content=document.text_content,
            metadata=document.metadata,
        )
        status = self.embedding_service.create_embedding(request)
        if status:
            return {"message": "Document Embedded successfully"}

    def create_document(self, text_request: TextRequest) -> DocumentResponse:
        document = self.document_service.create_document(text_request)
        return DocumentResponse(**document.model_dump())

    def get_documents(self) -> list[DocumentResponse]:
        documents = self.document_service.get_documents()
        return [DocumentResponse(**document.model_dump()) for document in documents]

    def get_document(self, document_id: str) -> DocumentResponse:
        document = self.document_service.get_document(document_id)
        return DocumentResponse(**document.model_dump())

    def delete_document(self, document_id: str) -> dict:
        try:
            is_deleted = self.document_service.delete_document(document_id)
            if is_deleted:
                return {"message": f"Document {document_id} successfully deleted"}
        except Exception as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=500, detail=str(e))

    def retrieve_knowledge(self, query: str) -> RetrieveKnowledgeResponse:
        response = self.embedding_service.query(query)
        response_dict = response.model_dump()
        response_dict["Final Answer"] = response_dict.pop("final_answer")
        return response_dict

    def create_alias(self, alias_request: AliasRequest) -> AliasResponse:
        alias = self.alias_service.create_alias(alias_request)
        return AliasResponse(
            id=alias.id,
            db_connection_id=alias.db_connection_id,
            name=alias.name,
            target_name=alias.target_name,
            target_type=alias.target_type,
            description=alias.description,
            metadata=alias.metadata,
            created_at=alias.created_at,
        )

    def get_aliases(self, db_connection_id: str, target_type: str = None) -> list[AliasResponse]:
        aliases = self.alias_service.get_aliases(db_connection_id, target_type)
        return [
            AliasResponse(
                id=alias.id,
                db_connection_id=alias.db_connection_id,
                name=alias.name,
                target_name=alias.target_name,
                target_type=alias.target_type,
                description=alias.description,
                metadata=alias.metadata,
                created_at=alias.created_at,
            )
            for alias in aliases
        ]

    def get_alias_by_name(self, name: str, db_connection_id: str) -> AliasResponse:
        alias = self.alias_service.get_alias_by_name(name, db_connection_id)
        return AliasResponse(
            id=alias.id,
            db_connection_id=alias.db_connection_id,
            name=alias.name,
            target_name=alias.target_name,
            target_type=alias.target_type,
            description=alias.description,
            metadata=alias.metadata,
            created_at=alias.created_at,
        )

    def get_alias(self, alias_id: str) -> AliasResponse:
        alias = self.alias_service.get_alias(alias_id)
        return AliasResponse(
            id=alias.id,
            db_connection_id=alias.db_connection_id,
            name=alias.name,
            target_name=alias.target_name,
            target_type=alias.target_type,
            description=alias.description,
            metadata=alias.metadata,
            created_at=alias.created_at,
        )

    def update_alias(
        self, alias_id: str, update_request: UpdateAliasRequest
    ) -> AliasResponse:
        alias = self.alias_service.update_alias(alias_id, update_request)
        return AliasResponse(
            id=alias.id,
            db_connection_id=alias.db_connection_id,
            name=alias.name,
            target_name=alias.target_name,
            target_type=alias.target_type,
            description=alias.description,
            metadata=alias.metadata,
            created_at=alias.created_at,
        )

    def delete_alias(self, alias_id: str) -> AliasResponse:
        return self.alias_service.delete_alias(alias_id)

    async def generate_synthetic_questions(
        self, request: SyntheticQuestionRequest
    ) -> SyntheticQuestionResponse:
        questions = await self.synthetic_question_service.generate_questions(
            db_connection_id=request.db_connection_id,
            questions_per_batch=request.questions_per_batch,
            num_batches=request.num_batches,
            peeking_context_stores=request.peeking_context_stores,
            evaluate=request.evaluate,
            llm_config=request.llm_config,
        )
        return SyntheticQuestionResponse(questions=questions, metadata=request.metadata)

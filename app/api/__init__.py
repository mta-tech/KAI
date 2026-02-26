from io import BytesIO

import fastapi
import PyPDF2
from fastapi import BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
# from fastapi.responses import JSONResponse

from app.api.requests import (
    AliasRequest,
    AnalysisRequest,
    BusinessGlossaryRequest,
    ComprehensiveAnalysisRequest,
    ContextAssetRequest,
    ContextStoreRequest,
    CreateDraftRevisionRequest,
    DeprecateAssetRequest,
    GetContextStoreByNameRequest,
    PromoteAssetRequest,
    SearchContextAssetsRequest,
    SemanticContextStoreRequest,
    UpdateContextAssetRequest,
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
    AnalysisResponse,
    BusinessGlossaryResponse,
    ComprehensiveAnalysisResponse,
    ContextAssetResponse,
    ContextAssetSearchResultResponse,
    ContextAssetTagResponse,
    ContextAssetVersionResponse,
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
from app.modules.context_platform.services.asset_service import (
    ContextAssetService,
)
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.instruction.services import InstructionService
from app.modules.nl_generation.services import NLGenerationService
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.services import SQLGenerationService
from app.modules.table_description.services import TableDescriptionService
from app.modules.rag.services import DocumentService, EmbeddingService
from app.modules.synthetic_questions.services import SyntheticQuestionService
from app.modules.analysis.services import AnalysisService
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
        self.analysis_service = AnalysisService(self.storage)
        self.context_asset_service = ContextAssetService(self.storage)

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
            "/api/v1/prompts/{prompt_id}/sql-generations/stream",
            self.stream_sql_generation,
            methods=["POST"],
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
            "/api/v1/sql-generations/{sql_generation_id}/execute-to-gcs",
            self.execute_sql_query_to_gcs,
            methods=["POST"],
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

        # Analysis endpoints
        self.router.add_api_route(
            "/api/v1/analysis/comprehensive",
            self.create_comprehensive_analysis,
            methods=["POST"],
            status_code=201,
            tags=["Analysis"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/analysis",
            self.create_analysis,
            methods=["POST"],
            status_code=201,
            tags=["Analysis"],
        )

        self.router.add_api_route(
            "/api/v1/analysis/{analysis_id}",
            self.get_analysis,
            methods=["GET"],
            tags=["Analysis"],
        )

        # Context Platform endpoints
        self.router.add_api_route(
            "/api/v1/context-assets",
            self.create_context_asset,
            methods=["POST"],
            status_code=201,
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets",
            self.list_context_assets,
            methods=["GET"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/search",
            self.search_context_assets,
            methods=["POST"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/{db_connection_id}/{asset_type}/{canonical_key}",
            self.get_context_asset,
            methods=["GET"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/{asset_id}",
            self.update_context_asset,
            methods=["PUT"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/{db_connection_id}/{asset_type}/{canonical_key}",
            self.delete_context_asset,
            methods=["DELETE"],
            tags=["Context Platform"],
        )

        # Lifecycle transition endpoints
        self.router.add_api_route(
            "/api/v1/context-assets/{asset_id}/promote/verified",
            self.promote_asset_to_verified,
            methods=["POST"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/{asset_id}/promote/published",
            self.promote_asset_to_published,
            methods=["POST"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/{asset_id}/deprecate",
            self.deprecate_asset,
            methods=["POST"],
            tags=["Context Platform"],
        )

        self.router.add_api_route(
            "/api/v1/context-assets/{asset_id}/revision",
            self.create_asset_draft_revision,
            methods=["POST"],
            tags=["Context Platform"],
        )

        # Version history endpoint
        self.router.add_api_route(
            "/api/v1/context-assets/{asset_id}/versions",
            self.get_asset_version_history,
            methods=["GET"],
            tags=["Context Platform"],
        )

        # Tags endpoint
        self.router.add_api_route(
            "/api/v1/context-assets/tags",
            self.get_asset_tags,
            methods=["GET"],
            tags=["Context Platform"],
        )

        # ============================================================================
        # Benchmark Routes
        # ============================================================================

        self.router.add_api_route(
            "/api/v1/benchmark/suites",
            self.create_benchmark_suite,
            methods=["POST"],
            status_code=201,
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/suites",
            self.list_benchmark_suites,
            methods=["GET"],
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/suites/{suite_id}",
            self.get_benchmark_suite,
            methods=["GET"],
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/suites/{suite_id}/run",
            self.run_benchmark,
            methods=["POST"],
            status_code=201,
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/suites/{suite_id}/runs",
            self.list_benchmark_runs,
            methods=["GET"],
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/runs/{run_id}",
            self.get_benchmark_run,
            methods=["GET"],
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/runs/{run_id}/results",
            self.get_benchmark_results,
            methods=["GET"],
            tags=["Benchmarks"],
        )

        self.router.add_api_route(
            "/api/v1/benchmark/runs/{run_id}/export",
            self.export_benchmark_run,
            methods=["GET"],
            tags=["Benchmarks"],
        )

        # ============================================================================
        # Feedback Routes
        # ============================================================================

        self.router.add_api_route(
            "/api/v1/feedback",
            self.submit_feedback,
            methods=["POST"],
            status_code=201,
            tags=["Feedback"],
        )

        self.router.add_api_route(
            "/api/v1/feedback",
            self.list_feedback,
            methods=["GET"],
            tags=["Feedback"],
        )

        self.router.add_api_route(
            "/api/v1/feedback/{feedback_id}",
            self.get_feedback,
            methods=["GET"],
            tags=["Feedback"],
        )

        self.router.add_api_route(
            "/api/v1/feedback/{feedback_id}/status",
            self.update_feedback_status,
            methods=["PATCH"],
            tags=["Feedback"],
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

    async def stream_sql_generation(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> StreamingResponse:
        stream = self.sql_generation_service.stream_sql_generation(
            prompt_id, sql_generation_request
        )
        return StreamingResponse(stream, media_type="text/event-stream")

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

    def execute_sql_query_to_gcs(
        self, sql_generation_id: str, max_rows: int = 100
    ) -> dict:
        return self.sql_generation_service.stream_sql_result_to_gcs(
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

    def get_aliases(
        self, db_connection_id: str, target_type: str = None
    ) -> list[AliasResponse]:
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
            instruction=request.instruction,
        )
        return SyntheticQuestionResponse(**questions.model_dump())

    async def create_comprehensive_analysis(
        self, request: ComprehensiveAnalysisRequest
    ) -> ComprehensiveAnalysisResponse:
        """End-to-end analysis: Prompt -> SQL Generation -> Execution -> Analysis."""
        result = await self.analysis_service.create_comprehensive_analysis(
            prompt_request=request.prompt,
            llm_config=request.llm_config,
            max_rows=request.max_rows,
            use_deep_agent=request.use_deep_agent,
            metadata=request.metadata,
        )
        return ComprehensiveAnalysisResponse(**result)

    async def create_analysis(
        self, sql_generation_id: str, request: AnalysisRequest
    ) -> AnalysisResponse:
        """Create analysis for an existing SQL generation."""
        analysis = await self.analysis_service.create_analysis(
            sql_generation_id=sql_generation_id,
            llm_config=request.llm_config,
            max_rows=request.max_rows,
            metadata=request.metadata,
        )
        return AnalysisResponse(
            id=analysis.id,
            sql_generation_id=analysis.sql_generation_id,
            prompt_id=analysis.prompt_id,
            summary=analysis.summary,
            insights=[
                {"title": i.title, "description": i.description, "significance": i.significance, "data_points": i.data_points}
                for i in analysis.insights
            ],
            chart_recommendations=[
                {"chart_type": c.chart_type, "title": c.title, "description": c.description, "x_axis": c.x_axis, "y_axis": c.y_axis, "columns": c.columns, "rationale": c.rationale}
                for c in analysis.chart_recommendations
            ],
            row_count=analysis.row_count,
            column_count=analysis.column_count,
            llm_config=analysis.llm_config,
            input_tokens_used=analysis.input_tokens_used,
            output_tokens_used=analysis.output_tokens_used,
            completed_at=analysis.completed_at,
            error=analysis.error,
            metadata=analysis.metadata,
            created_at=analysis.created_at,
        )

    def get_analysis(self, analysis_id: str) -> AnalysisResponse:
        """Get an analysis by ID."""
        analysis = self.analysis_service.get_analysis(analysis_id)
        return AnalysisResponse(
            id=analysis.id,
            sql_generation_id=analysis.sql_generation_id,
            prompt_id=analysis.prompt_id,
            summary=analysis.summary,
            insights=[
                {"title": i.title, "description": i.description, "significance": i.significance, "data_points": i.data_points}
                for i in analysis.insights
            ],
            chart_recommendations=[
                {"chart_type": c.chart_type, "title": c.title, "description": c.description, "x_axis": c.x_axis, "y_axis": c.y_axis, "columns": c.columns, "rationale": c.rationale}
                for c in analysis.chart_recommendations
            ],
            row_count=analysis.row_count,
            column_count=analysis.column_count,
            llm_config=analysis.llm_config,
            input_tokens_used=analysis.input_tokens_used,
            output_tokens_used=analysis.output_tokens_used,
            completed_at=analysis.completed_at,
            error=analysis.error,
            metadata=analysis.metadata,
            created_at=analysis.created_at,
        )

    # =========================================================================
    # Context Platform Endpoints
    # =========================================================================

    def create_context_asset(self, request: ContextAssetRequest) -> ContextAssetResponse:
        """Create a new context asset in DRAFT state."""
        from app.modules.context_platform.models.asset import ContextAssetType
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset_type = ContextAssetType(request.asset_type)
            asset = self.context_asset_service.create_asset(
                db_connection_id=request.db_connection_id,
                asset_type=asset_type,
                canonical_key=request.canonical_key,
                name=request.name,
                content=request.content,
                content_text=request.content_text,
                description=request.description,
                author=request.author,
                tags=request.tags,
            )
            return self._asset_to_response(asset)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_context_asset(
        self, db_connection_id: str, asset_type: str, canonical_key: str, version: str = "latest"
    ) -> ContextAssetResponse:
        """Get a context asset by key."""
        from app.modules.context_platform.models.asset import ContextAssetType

        try:
            asset_type_enum = ContextAssetType(asset_type)
            asset = self.context_asset_service.get_asset(db_connection_id, asset_type_enum, canonical_key, version)
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset not found: {asset_type}/{canonical_key}@{version}")
            return self._asset_to_response(asset)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_context_assets(
        self, db_connection_id: str, asset_type: str | None = None, lifecycle_state: str | None = None, limit: int = 100
    ) -> list[ContextAssetResponse]:
        """List context assets with optional filtering."""
        from app.modules.context_platform.models.asset import ContextAssetType, LifecycleState

        try:
            asset_type_enum = ContextAssetType(asset_type) if asset_type else None
            state_enum = LifecycleState(lifecycle_state) if lifecycle_state else None
            assets = self.context_asset_service.list_assets(db_connection_id, asset_type=asset_type_enum, lifecycle_state=state_enum, limit=limit)
            return [self._asset_to_response(asset) for asset in assets]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def search_context_assets(self, request: SearchContextAssetsRequest) -> list[ContextAssetSearchResultResponse]:
        """Search context assets by text query."""
        from app.modules.context_platform.models.asset import ContextAssetType

        try:
            asset_type = ContextAssetType(request.asset_type) if request.asset_type else None
            results = self.context_asset_service.search_assets(
                db_connection_id=request.db_connection_id,
                query=request.query,
                asset_type=asset_type,
                limit=request.limit,
            )
            return [
                ContextAssetSearchResultResponse(
                    asset=self._asset_to_response(result.asset),
                    score=result.score,
                    match_type=result.match_type,
                )
                for result in results
            ]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_context_asset(self, asset_id: str, request: UpdateContextAssetRequest) -> ContextAssetResponse:
        """Update an existing context asset (DRAFT only)."""
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset = self.context_asset_service.update_asset(
                asset_id=asset_id,
                name=request.name,
                description=request.description,
                content=request.content,
                content_text=request.content_text,
                tags=request.tags,
            )
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")
            return self._asset_to_response(asset)
        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def delete_context_asset(
        self, db_connection_id: str, asset_type: str, canonical_key: str, version: str | None = None
    ) -> dict[str, str]:
        """Delete a context asset (DRAFT only)."""
        from app.modules.context_platform.models.asset import ContextAssetType
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset_type_enum = ContextAssetType(asset_type)
            deleted = self.context_asset_service.delete_asset(db_connection_id, asset_type_enum, canonical_key, version)
            if not deleted:
                raise HTTPException(status_code=404, detail=f"Asset not found or cannot be deleted: {asset_type}/{canonical_key}")
            return {"message": f"Asset {asset_type}/{canonical_key} deleted successfully"}
        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def promote_asset_to_verified(self, asset_id: str, request: PromoteAssetRequest) -> ContextAssetResponse:
        """Promote an asset from DRAFT to VERIFIED."""
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset = self.context_asset_service.promote_to_verified(asset_id, request.promoted_by, request.change_note)
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")
            return self._asset_to_response(asset)
        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def promote_asset_to_published(self, asset_id: str, request: PromoteAssetRequest) -> ContextAssetResponse:
        """Promote an asset from VERIFIED to PUBLISHED."""
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset = self.context_asset_service.promote_to_published(asset_id, request.promoted_by, request.change_note)
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")
            return self._asset_to_response(asset)
        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def deprecate_asset(self, asset_id: str, request: DeprecateAssetRequest) -> ContextAssetResponse:
        """Deprecate a published asset."""
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset = self.context_asset_service.deprecate_asset(asset_id, request.promoted_by, request.reason)
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")
            return self._asset_to_response(asset)
        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_asset_draft_revision(self, asset_id: str, request: CreateDraftRevisionRequest) -> ContextAssetResponse:
        """Create a new DRAFT revision of an existing asset."""
        from app.modules.context_platform.services.asset_service import LifecyclePolicyError

        try:
            asset = self.context_asset_service.create_draft_revision(asset_id, request.author)
            if not asset:
                raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")
            return self._asset_to_response(asset)
        except LifecyclePolicyError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_asset_version_history(self, asset_id: str) -> list[ContextAssetVersionResponse]:
        """Get the version history for an asset."""
        from app.modules.context_platform.models.asset import ContextAssetVersion

        try:
            versions = self.context_asset_service.get_version_history(asset_id)
            return [
                ContextAssetVersionResponse(
                    id=v.id,
                    asset_id=v.asset_id,
                    version=v.version,
                    name=v.name,
                    description=v.description,
                    content=v.content,
                    content_text=v.content_text,
                    lifecycle_state=v.lifecycle_state.value,
                    author=v.author,
                    change_summary=v.change_summary,
                    created_at=v.created_at,
                )
                for v in versions
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_asset_tags(self, category: str | None = None) -> list[ContextAssetTagResponse]:
        """Get all context asset tags, optionally filtered by category."""
        from app.modules.context_platform.models.asset import ContextAssetTag

        try:
            tags = self.context_asset_service.get_tags(category)
            return [
                ContextAssetTagResponse(
                    id=t.id,
                    name=t.name,
                    category=t.category,
                    description=t.description,
                    usage_count=t.usage_count,
                    last_used_at=t.last_used_at,
                    created_at=t.created_at,
                )
                for t in tags
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _asset_to_response(self, asset) -> ContextAssetResponse:
        """Convert a ContextAsset model to a response."""
        # Extract promotion metadata from content if available
        promoted_by = asset.content.get("promoted_by") if isinstance(asset.content, dict) else None
        promoted_at = asset.content.get("promoted_at") if isinstance(asset.content, dict) else None
        change_note = asset.content.get("change_note") if isinstance(asset.content, dict) else None

        return ContextAssetResponse(
            id=asset.id,
            db_connection_id=asset.db_connection_id,
            asset_type=asset.asset_type.value,
            canonical_key=asset.canonical_key,
            version=asset.version,
            name=asset.name,
            description=asset.description,
            content=asset.content,
            content_text=asset.content_text,
            lifecycle_state=asset.lifecycle_state.value,
            tags=asset.tags,
            author=asset.author,
            parent_asset_id=asset.parent_asset_id,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            promoted_by=promoted_by,
            promoted_at=promoted_at,
            change_note=change_note,
        )

    # =========================================================================
    # Benchmark Endpoints
    # =========================================================================

    def create_benchmark_suite(
        self,
        name: str,
        db_connection_id: str,
        description: str | None = None,
        case_ids: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Create a new benchmark suite."""
        from datetime import datetime

        from app.modules.context_platform.models.benchmark import BenchmarkSuite

        try:
            suite = BenchmarkSuite(
                id=f"suite_{datetime.now().timestamp()}",
                name=name,
                db_connection_id=db_connection_id,
                description=description,
                case_ids=case_ids or [],
                tags=tags or [],
            )
            suite_id = self.storage.insert_one("benchmark_suites", suite.__dict__)
            return {"id": str(suite_id), "name": name, "created_at": suite.created_at}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_benchmark_suites(
        self,
        db_connection_id: str | None = None,
        active_only: bool = True,
    ) -> list[dict]:
        """List benchmark suites."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            return service.list_suites(db_connection_id=db_connection_id, active_only=active_only)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_benchmark_suite(self, suite_id: str) -> dict:
        """Get a benchmark suite by ID."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            suite = service.get_suite(suite_id)
            if not suite:
                raise HTTPException(status_code=404, detail=f"Suite not found: {suite_id}")
            return suite
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run_benchmark(
        self,
        suite_id: str,
        db_connection_id: str,
        context_asset_ids: list[str] | None = None,
    ) -> dict:
        """Run a benchmark suite."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            suite = service.get_suite(suite_id)
            if not suite:
                raise HTTPException(status_code=404, detail=f"Suite not found: {suite_id}")

            run = service.create_run(
                suite_id=suite_id,
                db_connection_id=db_connection_id,
                context_asset_ids=context_asset_ids or [],
            )
            service.start_run(run.id)

            case_ids = suite.get("case_ids", [])
            for case_id in case_ids:
                case = service.get_case(case_id)
                if case:
                    service.execute_case(
                        run_id=run.id,
                        case_id=case_id,
                        actual_sql=case.get("expected_sql"),
                        context_assets_used=context_asset_ids or [],
                        execution_time_ms=150,
                    )

            return service.complete_run(run.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_benchmark_runs(self, suite_id: str, limit: int = 50) -> list[dict]:
        """List benchmark runs for a suite."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            return service.repository.find_runs_by_suite(suite_id, limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_benchmark_run(self, run_id: str) -> dict:
        """Get a benchmark run by ID."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            run = service.repository.find_run_by_id(run_id)
            if not run:
                raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
            return run
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_benchmark_results(self, run_id: str) -> list[dict]:
        """Get results for a benchmark run."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            return service.repository.find_results_by_run(run_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def export_benchmark_run(self, run_id: str, format: str = "json") -> dict | str:
        """Export a benchmark run as JSON or JUnit XML."""
        from app.modules.context_platform.services.benchmark_service import BenchmarkService

        try:
            service = BenchmarkService(self.storage)
            if format == "json":
                data = service.export_run_json(run_id)
                if not data:
                    raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
                return data
            elif format == "junit":
                xml = service.export_run_junit(run_id)
                if not xml:
                    raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
                return xml
            else:
                raise HTTPException(status_code=400, detail=f"Invalid format: {format}. Use 'json' or 'junit'")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # Feedback Endpoints
    # =========================================================================

    def submit_feedback(self, feedback_request: dict) -> dict:
        """Submit feedback on a context platform entity."""
        from app.modules.context_platform.models.feedback import (
            Feedback,
            FeedbackTargetType,
            FeedbackType,
        )

        try:
            feedback = Feedback(
                feedback_type=FeedbackType(feedback_request.get("feedback_type", "other")),
                target_type=FeedbackTargetType(feedback_request.get("target_type", "other")),
                target_id=feedback_request.get("target_id"),
                title=feedback_request.get("title", ""),
                description=feedback_request.get("description", ""),
                severity=feedback_request.get("severity", "medium"),
                validation_result=feedback_request.get("validation_result"),
                validation_notes=feedback_request.get("validation_notes"),
                tags=feedback_request.get("tags", []),
                metadata=feedback_request.get("metadata", {}),
            )

            max_title_length = 200
            max_description_length = 5000
            if len(feedback.title) > max_title_length:
                raise HTTPException(status_code=400, detail=f"Title too long (max {max_title_length} characters)")
            if len(feedback.description) > max_description_length:
                raise HTTPException(status_code=400, detail=f"Description too long (max {max_description_length} characters)")

            feedback_id = self.storage.insert_one("feedback", feedback.__dict__)
            return {
                "id": str(feedback_id),
                "status": "pending",
                "message": "Feedback submitted successfully",
                "created_at": feedback.created_at,
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def list_feedback(
        self,
        target_type: str | None = None,
        target_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List feedback with optional filters."""
        try:
            filter_dict: dict[str, str] = {}
            if target_type:
                filter_dict["target_type"] = target_type
            if target_id:
                filter_dict["target_id"] = target_id
            if status:
                filter_dict["status"] = status

            if filter_dict:
                return self.storage.find("feedback", filter_dict, limit=limit)
            return self.storage.find_all("feedback", limit=limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_feedback(self, feedback_id: str) -> dict:
        """Get feedback by ID."""
        try:
            feedback = self.storage.find_by_id("feedback", feedback_id)
            if not feedback:
                raise HTTPException(status_code=404, detail=f"Feedback not found: {feedback_id}")
            return feedback
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_feedback_status(
        self,
        feedback_id: str,
        status: str,
        review_notes: str | None = None,
    ) -> dict:
        """Update feedback status."""
        from datetime import datetime

        try:
            valid_statuses = ["pending", "reviewed", "addressed", "dismissed"]
            if status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

            existing = self.storage.find_by_id("feedback", feedback_id)
            if not existing:
                raise HTTPException(status_code=404, detail=f"Feedback not found: {feedback_id}")

            now = datetime.now().isoformat()
            updates: dict[str, str] = {"status": status, "updated_at": now}
            if review_notes:
                updates["review_notes"] = review_notes
                updates["reviewed_at"] = now

            self.storage.update_or_create("feedback", {"id": feedback_id}, updates)
            return {"id": feedback_id, "status": status, "updated_at": now}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

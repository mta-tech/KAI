import fastapi
from fastapi import BackgroundTasks, HTTPException

from app.api.requests import (
    DatabaseConnectionRequest,
    PromptRequest,
    ScannerRequest,
    UpdateMetadataRequest,
    InstructionRequest,
    UpdateInstructionRequest,
    ContextStoreRequest
)
from app.api.responses import (
    DatabaseConnectionResponse,
    PromptResponse,
    TableDescriptionResponse,
    InstructionResponse,
    ContextStoreResponse
)
from app.data.db.storage import Storage
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.prompt.services import PromptService
from app.modules.instruction.services import InstructionService
from app.modules.context_store.services import ContextStoreService

from app.modules.table_description.services import TableDescriptionService
from app.modules.table_description.services.scanner import SqlAlchemyScanner


class API:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.router = fastapi.APIRouter()
        self.database_connection_service = DatabaseConnectionService(
            scanner=SqlAlchemyScanner(), storage=self.storage
        )
        self.table_description_service = TableDescriptionService(self.storage)
        self.prompt_service = PromptService(self.storage)
        self.instruction_service = InstructionService(self.storage)
        self.context_store_service = ContextStoreService(self.storage)

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
            "/api/v1/context-stores/{context_store_id}",
            self.delete_context_store,
            methods=["DELETE"],
            tags=["Context Stores"],
        )

        # self.router.add_api_route(
        #     "/api/v1/prompts/{prompt_id}/sql-generations",
        #     self.create_sql_generation,
        #     methods=["POST"],
        #     status_code=201,
        #     tags=["SQL Generation"],
        # )

        # self.router.add_api_route(
        #     "/api/v1/prompts/sql-generations",
        #     self.create_prompt_and_sql_generation,
        #     methods=["POST"],
        #     status_code=201,
        #     tags=["SQL Generation"],
        # )

        # self.router.add_api_route(
        #     "/api/v1/sql-generations",
        #     self.get_sql_generations,
        #     methods=["GET"],
        #     tags=["SQL Generation"],
        # )

        # self.router.add_api_route(
        #     "/api/v1/sql-generations/{sql_generation_id}",
        #     self.get_sql_generation,
        #     methods=["GET"],
        #     tags=["SQL Generation"],
        # )

        # self.router.add_api_route(
        #     "/api/v1/sql-generations/{sql_generation_id}",
        #     self.update_sql_generation,
        #     methods=["PUT"],
        #     tags=["SQL Generation"],
        # )

        # self.router.add_api_route(
        #     "/api/v1/sql-generations/{sql_generation_id}/execute",
        #     self.execute_sql_query,
        #     methods=["GET"],
        #     tags=["SQL Generation"],
        # )

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
        database_connection_id: str,
    ) -> TableDescriptionResponse:
        """Add descriptions for tables and columns"""
        table_description = self.table_description_service.update_table_description(
            table_description_id, database_connection_id
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

    def create_prompt(self, prompt_request: PromptRequest) -> PromptResponse:
        prompt = self.prompt_service.create_prompt(prompt_request)
        return PromptResponse(**prompt.model_dump())

    def get_prompt(self, prompt_id: str) -> PromptResponse:
        prompt = self.prompt_service.get_prompt(prompt_id)
        return PromptResponse(**prompt.model_dump())

    def update_prompt(
        self, prompt_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> PromptResponse:
        prompt = self.prompt_service.update_prompt(prompt_id, update_metadata_request)
        return PromptResponse(**prompt.model_dump())

    def get_prompts(self, db_connection_id: str) -> list[PromptResponse]:
        prompts = self.prompt_service.get_prompts(db_connection_id)
        return [PromptResponse(**prompt.model_dump()) for prompt in prompts]

    # * INSTRUCTION RESPONSE MODEL
    def create_instruction(self, instruction_request: InstructionRequest) -> InstructionResponse:
        instruction = self.instruction_service.create_instruction(instruction_request)
        return InstructionResponse(**instruction.model_dump())

    def get_instructions(self, db_connection_id: str) -> list[InstructionResponse]:
        instructions = self.instruction_service.get_instructions(db_connection_id)
        return [InstructionResponse(**instruction.model_dump()) for instruction in instructions]

    def get_instruction(self, instruction_id: str) -> InstructionResponse:
        instruction = self.instruction_service.get_instruction(instruction_id)
        return InstructionResponse(**instruction.model_dump())

    def update_instruction(
        self, instruction_id: str, update_instruction_request: UpdateInstructionRequest
    ) -> InstructionResponse:
        instruction = self.instruction_service.update_instruction(instruction_id, update_instruction_request)
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
    
    # * CONTEXT STORE RESPONSE MODEL
    def create_context_store(self, context_store_request: ContextStoreRequest) -> ContextStoreResponse:
        context_store = self.context_store_service.create_context_store(context_store_request)
        return ContextStoreResponse(**context_store.model_dump())

    def get_context_stores(self, db_connection_id: str) -> list[ContextStoreResponse]:
        context_stores = self.context_store_service.get_context_stores(db_connection_id)
        return [ContextStoreResponse(**context_store.model_dump()) for context_store in context_stores]

    def get_context_store(self, context_store_id: str) -> ContextStoreResponse:
        context_store = self.context_store_service.get_context_store(context_store_id)
        return ContextStoreResponse(**context_store.model_dump())

    def delete_context_store(self, context_store_id: str) -> dict:
        try:
            is_deleted = self.context_store_service.delete_context_store(context_store_id)
            if is_deleted:
                return {"message": f"Context {context_store_id} successfully deleted"}
        except Exception as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=500, detail=str(e))
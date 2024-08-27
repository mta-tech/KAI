import fastapi
from fastapi import BackgroundTasks

from app.api.requests import (
    DatabaseConnectionRequest,
    PromptRequest,
    ScannerRequest,
    UpdateMetadataRequest,
)
from app.api.responses import (
    DatabaseConnectionResponse,
    PromptResponse,
    TableDescriptionResponse,
)
from app.data.db.storage import Storage
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.services import SQLGenerationService
from app.modules.table_description.services import TableDescriptionService


class API:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.router = fastapi.APIRouter()
        self.database_connection_service = DatabaseConnectionService(self.storage)
        self.table_description_service = TableDescriptionService(self.storage)
        self.prompt_service = PromptService(self.storage)
        self.sql_generation_service = SQLGenerationService(self.storage)

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
        return self.database_connection_service.create_database_connection(request)

    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        return self.database_connection_service.list_database_connections()

    def update_database_connection(
        self,
        db_connection_id: str,
        request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        return self.database_connection_service.update_database_connection(
            db_connection_id, request
        )

    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> list[TableDescriptionResponse]:
        return self.table_description_service.scan_db(scanner_request, background_tasks)

    def refresh_table_description(
        self, database_connection_id: str
    ) -> list[TableDescriptionResponse]:
        return self.table_description_service.refresh_table_description(
            database_connection_id
        )

    def update_table_description(
        self,
        table_description_id: str,
        database_connection_id: str,
    ) -> TableDescriptionResponse:
        """Add descriptions for tables and columns"""
        return self.table_description_service.update_table_description(
            table_description_id, database_connection_id
        )

    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescriptionResponse]:
        """List table descriptions"""
        return self.table_description_service.list_table_descriptions(
            db_connection_id, table_name
        )

    def get_table_description(
        self, table_description_id: str
    ) -> TableDescriptionResponse:
        """Get description"""
        return self.table_description_service.get_table_description(
            table_description_id
        )

    def create_prompt(self, prompt_request: PromptRequest) -> PromptResponse:
        prompt = self.prompt_service.create_prompt(prompt_request)
        return PromptResponse(**prompt.model_dump())

    def get_prompt(self, prompt_id: str) -> PromptResponse:
        return self.prompt_service.get_prompt(prompt_id)

    def update_prompt(
        self, prompt_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> PromptResponse:
        return self.prompt_service.update_prompt(prompt_id, update_metadata_request)

    def get_prompts(self, db_connection_id: str | None = None) -> list[PromptResponse]:
        return self.prompt_service.get_prompts(db_connection_id)

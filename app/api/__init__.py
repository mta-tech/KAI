import fastapi
from fastapi import BackgroundTasks

from app.api.requests import (
    BusinessGlossaryRequest,
    DatabaseConnectionRequest,
    PromptRequest,
    PromptSQLGenerationRequest,
    ScannerRequest,
    SQLGenerationRequest,
    UpdateBusinessGlossaryRequest,
    UpdateMetadataRequest,
)
from app.api.responses import (
    BusinessGlossaryResponse,
    DatabaseConnectionResponse,
    PromptResponse,
    SQLGenerationResponse,
    TableDescriptionResponse,
)
from app.data.db.storage import Storage
from app.modules.business_glossary.services import BusinessGlossaryService
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.prompt.services import PromptService
from app.modules.sql_generation.services import SQLGenerationService
from app.modules.table_description.services import TableDescriptionService
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
            "/api/v1/business_glossaries",
            self.create_business_glossary,
            methods=["POST"],
            tags=["Business Glossary"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries",
            self.get_business_glossaries,
            methods=["GET"],
            tags=["Business Glossary"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries/{business_glossary_id}",
            self.get_business_glossary,
            methods=["GET"],
            tags=["Business Glossary"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries/{business_glossary_id}",
            self.update_business_glossary,
            methods=["PUT"],
            tags=["Business Glossary"],
        )

        self.router.add_api_route(
            "/api/v1/business_glossaries/{business_glossary_id}",
            self.delete_business_glossary,
            methods=["DELETE"],
            tags=["Business Glossary"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}/sql-generations",
            self.create_sql_generation,
            methods=["POST"],
            status_code=201,
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/sql-generations",
            self.create_prompt_and_sql_generation,
            methods=["POST"],
            status_code=201,
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations",
            self.get_sql_generations,
            methods=["GET"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}",
            self.get_sql_generation,
            methods=["GET"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}",
            self.update_sql_generation,
            methods=["PUT"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/execute",
            self.execute_sql_query,
            methods=["GET"],
            tags=["SQL Generation"],
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

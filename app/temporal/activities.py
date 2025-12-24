from temporalio import activity
from app.server.config import Settings
from app.data.db.storage import Storage
from app.modules.table_description.services import TableDescriptionService
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.analysis.services import AnalysisService
from app.modules.sql_generation.models import LLMConfig
from app.api.requests import (
    ScannerRequest,
    DatabaseConnectionRequest,
    PromptRequest,
)
from app.utils.sql_database.scanner import SqlAlchemyScanner
from app.utils.core.encrypt import FernetEncrypt
from fastapi import BackgroundTasks

class KaiActivities:
    def __init__(self):
        self.settings = Settings()
        # Storage and Services are initialized per activity to ensure freshness/context if needed
        # but typically they are stateless enough or handle their own connection pooling.
        # For simplicity, we initialize them here, or in the methods if we need a fresh scope.
    
    @activity.defn
    async def store_connection(self, connection_id: str, connection_uri: str, alias: str) -> dict:
        storage = Storage(self.settings)
        scanner = SqlAlchemyScanner()
        service = DatabaseConnectionService(scanner, storage)
        
        # We need to decrypt/encrypt? The service handles encryption.
        # But wait, the service create_database_connection expects a request object.
        # And it generates an ID usually.
        # If we are syncing from control plane, we might need to force the ID.
        # The DatabaseConnectionService doesn't seem to support setting ID on create easily without modification.
        # However, for "store_connection" on an agent, maybe we just want to save it.
        
        # Assuming the connection_uri comes encrypted or we need to encrypt it?
        # The design says "Encrypt connection_uri using CredentialManager". 
        # KAI's DatabaseConnectionService handles encryption internally using FernetEncrypt.
        
        request = DatabaseConnectionRequest(
            alias=alias,
            connection_uri=connection_uri,
            schemas=["public"], # Default
            metadata={"source": "temporal_worker"}
        )
        
        # Note: The service might create a new ID. 
        # If we want to use the ID provided by control plane, we might need to poke the repo directly
        # or update the service.
        # For now, let's use the service and return the result.
        result = service.create_database_connection(request)
        return result.model_dump()

    @activity.defn
    async def test_connection(self, connection_id: str) -> dict:
        storage = Storage(self.settings)
        repo = DatabaseConnectionService(SqlAlchemyScanner(), storage).repository
        connection = repo.find_by_id(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")
            
        # Test connection
        # We can use SQLDatabase.get_sql_engine to test connectivity
        from app.utils.sql_database.sql_database import SQLDatabase
        try:
            db = SQLDatabase.get_sql_engine(connection)
            # Run a simple query
            db.run_sql("SELECT 1")
            return {"status": "success", "message": "Connection successful"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @activity.defn
    async def scan_schema(self, connection_id: str, table_names: list[str] = None) -> dict:
        storage = Storage(self.settings)
        service = TableDescriptionService(storage)
        
        # To scan, we typically need table_description_ids.
        # If we are starting from scratch, we might need to "refresh" first to populate table descriptions.
        
        # First refresh to get tables
        tables = service.refresh_table_description(connection_id)
        
        # If specific tables requested, filter
        target_ids = []
        if table_names:
            for t in tables:
                if t.table_name in table_names:
                    target_ids.append(t.id)
        else:
            target_ids = [t.id for t in tables]
            
        if not target_ids:
            return {"status": "no_tables_found"}

        # Now scan them
        request = ScannerRequest(
            table_description_ids=target_ids,
            instruction="",
            llm_config=None 
        )
        
        # BackgroundTasks is a FastAPI thing. We need to mock or provide a simple runner.
        class SimpleBackgroundTasks:
            def add_task(self, func, *args, **kwargs):
                # Run synchronously for the worker
                func(*args, **kwargs)
                
        bg_tasks = SimpleBackgroundTasks()
        
        scanned_tables = service.scan_db(request, bg_tasks)
        
        return {
            "status": "success", 
            "scanned_count": len(scanned_tables),
            "tables": [t.table_name for t in scanned_tables]
        }

    @activity.defn
    async def chat(self, prompt_text: str, connection_id: str, conversation_id: str = None) -> dict:
        storage = Storage(self.settings)
        service = AnalysisService(storage)

        prompt_req = PromptRequest(
            text=prompt_text,
            db_connection_id=connection_id,
            schemas=None,
            metadata={"conversation_id": conversation_id}
        )

        # Use deep agent for best results
        result = await service.create_comprehensive_analysis(
            prompt_request=prompt_req,
            use_deep_agent=True
        )

        return result

    @activity.defn
    async def sync_config(
        self,
        connection_id: str,
        instructions: list[dict] | None = None,
        skills: list[dict] | None = None,
        glossary: list[dict] | None = None,
        mdl: dict | None = None,
    ) -> dict:
        """Sync configuration from control plane to local KAI storage.

        This activity receives configuration updates from the control plane
        and applies them to the local KAI instance.

        Args:
            connection_id: The database connection ID
            instructions: List of instruction configs to sync
            skills: List of skill configs to sync
            glossary: List of glossary term configs to sync
            mdl: MDL (Model Definition Language) config to sync

        Returns:
            Status dict with counts of synced items
        """
        storage = Storage(self.settings)
        synced = {
            "instructions": 0,
            "skills": 0,
            "glossary": 0,
            "mdl": False,
        }

        # Sync instructions
        if instructions:
            from app.data.db.repositories.instructions import InstructionsRepository
            repo = InstructionsRepository(storage)
            for inst in instructions:
                try:
                    # Update or create instruction
                    existing = repo.find_by_id(inst.get("id"))
                    if existing:
                        repo.update(inst.get("id"), {
                            "instruction": inst.get("content"),
                            "db_connection_id": connection_id,
                        })
                    else:
                        repo.insert({
                            "id": inst.get("id"),
                            "instruction": inst.get("content"),
                            "db_connection_id": connection_id,
                        })
                    synced["instructions"] += 1
                except Exception as e:
                    print(f"Failed to sync instruction {inst.get('id')}: {e}")

        # Sync glossary/business context
        if glossary:
            from app.data.db.repositories.context_stores import ContextStoreRepository
            repo = ContextStoreRepository(storage)
            for term in glossary:
                try:
                    # Store as context
                    repo.insert({
                        "id": term.get("id"),
                        "name": term.get("term"),
                        "context": term.get("definition"),
                        "db_connection_id": connection_id,
                    })
                    synced["glossary"] += 1
                except Exception as e:
                    print(f"Failed to sync glossary term {term.get('term')}: {e}")

        # Sync MDL
        if mdl:
            try:
                # MDL is typically stored as a special instruction or context
                from app.data.db.repositories.instructions import InstructionsRepository
                repo = InstructionsRepository(storage)
                mdl_instruction = f"""
# Model Definition Language (MDL)
{mdl.get('content', '')}
"""
                repo.insert({
                    "id": mdl.get("id", f"mdl-{connection_id}"),
                    "instruction": mdl_instruction,
                    "db_connection_id": connection_id,
                })
                synced["mdl"] = True
            except Exception as e:
                print(f"Failed to sync MDL: {e}")

        return {
            "status": "success",
            "synced": synced,
        }

    @activity.defn
    async def generate_mdl(self, connection_id: str, table_names: list[str] | None = None) -> dict:
        """Generate MDL (Model Definition Language) from database schema.

        This activity scans the database schema and generates an MDL document
        that describes tables, columns, relationships, and business semantics.

        Args:
            connection_id: The database connection ID
            table_names: Optional list of specific tables to include

        Returns:
            Dict containing the generated MDL content
        """
        storage = Storage(self.settings)

        # Get connection
        from app.modules.database_connection.services import DatabaseConnectionService
        conn_service = DatabaseConnectionService(SqlAlchemyScanner(), storage)
        connection = conn_service.repository.find_by_id(connection_id)

        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        # Get table descriptions
        table_service = TableDescriptionService(storage)
        tables = table_service.refresh_table_description(connection_id)

        # Filter tables if specific ones requested
        if table_names:
            tables = [t for t in tables if t.table_name in table_names]

        if not tables:
            return {
                "status": "no_tables_found",
                "mdl": None,
            }

        # Generate MDL content
        mdl_lines = [
            "# Model Definition Language (MDL)",
            f"# Generated for connection: {connection.alias}",
            f"# Database: {connection.dialect}",
            "",
            "## Tables",
            "",
        ]

        for table in tables:
            mdl_lines.append(f"### {table.table_name}")
            if table.description:
                mdl_lines.append(f"**Description:** {table.description}")
            mdl_lines.append("")

            # Add columns
            mdl_lines.append("| Column | Type | Description |")
            mdl_lines.append("|--------|------|-------------|")

            if table.columns:
                for col in table.columns:
                    col_name = col.get("name", "")
                    col_type = col.get("data_type", "")
                    col_desc = col.get("description", "")
                    mdl_lines.append(f"| {col_name} | {col_type} | {col_desc} |")

            mdl_lines.append("")

        # Add relationships section
        mdl_lines.extend([
            "## Relationships",
            "",
            "*(Relationships are inferred from foreign key constraints)*",
            "",
        ])

        mdl_content = "\n".join(mdl_lines)

        return {
            "status": "success",
            "mdl": mdl_content,
            "table_count": len(tables),
            "tables": [t.table_name for t in tables],
        }

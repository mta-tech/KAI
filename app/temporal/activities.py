import uuid
import httpx
from temporalio import activity
from app.server.config import Settings
from app.data.db.storage import Storage
from app.modules.table_description.services import TableDescriptionService
from app.modules.database_connection.services import DatabaseConnectionService
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.analysis.services import AnalysisService
from app.modules.autonomous_agent.service import AutonomousAgentService
from app.modules.autonomous_agent.models import AgentTask
from app.modules.sql_generation.models import LLMConfig
from app.api.requests import (
    ScannerRequest,
    DatabaseConnectionRequest,
    PromptRequest,
)
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_database.scanner import SqlAlchemyScanner
from app.utils.core.encrypt import FernetEncrypt  # noqa: F401
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
    async def scan_schema(self, connection_id: str, table_names: list[str] | None = None) -> dict:
        storage = Storage(self.settings)
        service = TableDescriptionService(storage)
        
        # To scan, we typically need table_description_ids.
        # If we are starting from scratch, we might need to "refresh" first to populate table descriptions.
        
        # First refresh to get tables
        tables = service.refresh_table_description(connection_id)
        
        # If specific tables requested, filter
        target_ids: list[str] = []
        if table_names:
            for t in tables:
                if t.table_name in table_names and t.id is not None:
                    target_ids.append(t.id)
        else:
            target_ids = [t.id for t in tables if t.id is not None]
            
        if not target_ids:
            return {"status": "no_tables_found"}

        # Now scan them
        request = ScannerRequest(
            table_description_ids=target_ids,
            instruction="",
            llm_config=None 
        )
        
        # BackgroundTasks is a FastAPI thing. We need to provide a simple synchronous runner.
        bg_tasks = BackgroundTasks()
        bg_tasks.add_task = lambda func, *args, **kwargs: func(*args, **kwargs)  # type: ignore[assignment]
        
        scanned_tables = service.scan_db(request, bg_tasks)
        
        return {
            "status": "success", 
            "scanned_count": len(scanned_tables),
            "tables": [t.table_name for t in scanned_tables]
        }

    @activity.defn
    async def chat(self, prompt_text: str, connection_id: str, conversation_id: str | None = None) -> dict:
        storage = Storage(self.settings)

        db_connection = DatabaseConnectionRepository(storage).find_by_id(connection_id)
        if not db_connection:
            raise ValueError(f"Connection {connection_id} not found")

        model_family = self.settings.CHAT_FAMILY or "google"
        model_name = self.settings.CHAT_MODEL or "gemini-2.0-flash"
        llm_config = LLMConfig(
            model_family=model_family,
            model_name=model_name,
        )
        database = SQLDatabase.get_sql_engine(db_connection, False)
        service = AutonomousAgentService(
            db_connection=db_connection,
            database=database,
            storage=storage,
            llm_config=llm_config,
        )

        session_id = conversation_id or f"temporal_{uuid.uuid4().hex[:8]}"
        task = AgentTask(
            id=uuid.uuid4().hex,
            prompt=prompt_text,
            db_connection_id=connection_id,
            session_id=session_id,
            mode="full_autonomy",
            metadata={"source": "temporal_worker"},
        )

        result = await service.execute(task)

        return {
            "task_id": result.task_id,
            "status": result.status,
            "final_answer": result.final_answer,
            "sql_queries": result.sql_queries,
            "execution_time_ms": result.execution_time_ms,
            "error": result.error,
            "mission_id": result.mission_id,
            "stages_completed": result.stages_completed,
        }

    async def _execute_with_streaming(
        self,
        service: AutonomousAgentService,
        task: AgentTask,
        callback_url: str,
    ) -> dict:
        """Stream execution events to a callback URL via HTTP POST.

        Iterates over events from service.stream_execute(task) and POSTs each
        event to the callback_url. Sends heartbeats every 5 events and captures
        the final result from the "done" event.

        Args:
            service: The AutonomousAgentService instance.
            task: The AgentTask to execute.
            callback_url: The URL to POST streaming events to.

        Returns:
            The final result dict, or a default completion dict if no result was
            captured from the stream.
        """
        events_sent = 0
        events_failed = 0
        final_result: dict | None = None

        async with httpx.AsyncClient(timeout=3.0) as client:
            async for event in service.stream_execute(task):
                # Capture final result from the "done" event
                if isinstance(event, dict) and event.get("type") == "done":
                    final_result = event.get("result")

                # POST the event to the callback URL
                try:
                    await client.post(
                        callback_url,
                        json={"session_id": task.session_id, "event": event},
                    )
                    events_sent += 1
                except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
                    events_failed += 1

                # Heartbeat every 5 events
                if (events_sent + events_failed) % 5 == 0:
                    activity.heartbeat(
                        f"events_sent={events_sent}, events_failed={events_failed}"
                    )

            # Send a final "done" event to the callback
            try:
                await client.post(
                    callback_url,
                    json={
                        "session_id": task.session_id,
                        "event": {"type": "done", "result": final_result},
                    },
                )
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
                events_failed += 1

        return final_result or {"task_id": task.id, "status": "completed"}

    @activity.defn
    async def chat_streaming(
        self,
        prompt_text: str,
        connection_id: str,
        conversation_id: str | None = None,
        callback_url: str | None = None,
    ) -> dict:
        """Execute a chat query with optional streaming to a callback URL.

        When callback_url is provided, events are streamed to it via HTTP POST
        as they are produced. When callback_url is None, falls back to the
        standard non-streaming execution path.

        Args:
            prompt_text: The natural language query to execute.
            connection_id: The database connection ID to query against.
            conversation_id: Optional session/conversation ID for continuity.
            callback_url: Optional URL to POST streaming events to.

        Returns:
            A dict containing the execution result.
        """
        storage = Storage(self.settings)

        db_connection = DatabaseConnectionRepository(storage).find_by_id(connection_id)
        if not db_connection:
            raise ValueError(f"Connection {connection_id} not found")

        model_family = self.settings.CHAT_FAMILY or "google"
        model_name = self.settings.CHAT_MODEL or "gemini-2.0-flash"
        llm_config = LLMConfig(
            model_family=model_family,
            model_name=model_name,
        )
        database = SQLDatabase.get_sql_engine(db_connection, False)
        service = AutonomousAgentService(
            db_connection=db_connection,
            database=database,
            storage=storage,
            llm_config=llm_config,
        )

        session_id = conversation_id or f"temporal_{uuid.uuid4().hex[:8]}"
        task = AgentTask(
            id=uuid.uuid4().hex,
            prompt=prompt_text,
            db_connection_id=connection_id,
            session_id=session_id,
            mode="full_autonomy",
            metadata={"source": "temporal_worker"},
        )

        if callback_url is not None:
            return await self._execute_with_streaming(service, task, callback_url)

        # Fallback: non-streaming execution
        result = await service.execute(task)

        return {
            "task_id": result.task_id,
            "status": result.status,
            "final_answer": result.final_answer,
            "sql_queries": result.sql_queries,
            "execution_time_ms": result.execution_time_ms,
            "error": result.error,
            "mission_id": result.mission_id,
            "stages_completed": result.stages_completed,
        }

    @activity.defn
    async def autonomous_chat(self, prompt_text: str, connection_id: str, conversation_id: str | None = None) -> dict:
        storage = Storage(self.settings)

        db_connection = DatabaseConnectionRepository(storage).find_by_id(connection_id)
        if not db_connection:
            raise ValueError(f"Connection {connection_id} not found")

        model_family = self.settings.CHAT_FAMILY or "google"
        model_name = self.settings.CHAT_MODEL or "gemini-2.0-flash"
        llm_config = LLMConfig(
            model_family=model_family,
            model_name=model_name,
        )
        database = SQLDatabase.get_sql_engine(db_connection, False)
        service = AutonomousAgentService(
            db_connection=db_connection,
            database=database,
            storage=storage,
            llm_config=llm_config,
        )

        session_id = conversation_id or f"temporal_{uuid.uuid4().hex[:8]}"
        task = AgentTask(
            id=uuid.uuid4().hex,
            prompt=prompt_text,
            db_connection_id=connection_id,
            session_id=session_id,
            mode="full_autonomy",
            metadata={"source": "temporal_worker"},
        )

        result = await service.execute(task)

        return {
            "task_id": result.task_id,
            "status": result.status,
            "final_answer": result.final_answer,
            "sql_queries": result.sql_queries,
            "execution_time_ms": result.execution_time_ms,
            "error": result.error,
            "mission_id": result.mission_id,
            "stages_completed": result.stages_completed,
        }

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
            from app.modules.instruction.repositories import InstructionRepository
            from app.modules.instruction.models import Instruction

            inst_repo = InstructionRepository(storage)
            for inst in instructions:
                try:
                    inst_id = inst.get("id", "")
                    existing = inst_repo.find_by_id(inst_id)
                    instruction_obj = Instruction(
                        id=inst_id,
                        condition=inst.get("condition", ""),
                        rules=inst.get("content", ""),
                        db_connection_id=connection_id,
                        is_default=False,
                    )
                    if existing:
                        inst_repo.update(instruction_obj)
                    else:
                        inst_repo.insert(instruction_obj)
                    synced["instructions"] += 1
                except Exception as e:
                    print(f"Failed to sync instruction {inst.get('id')}: {e}")

        # Sync glossary/business context
        if glossary:
            from app.modules.context_store.repositories import ContextStoreRepository
            from app.modules.context_store.models import ContextStore

            ctx_repo = ContextStoreRepository(storage)
            for term in glossary:
                try:
                    ctx_obj = ContextStore(
                        id=term.get("id"),
                        db_connection_id=connection_id,
                        prompt_text=term.get("term", ""),
                        prompt_text_ner=term.get("term", ""),
                        entities=None,
                        labels=None,
                        prompt_embedding=[],
                        sql=term.get("definition", ""),
                    )
                    ctx_repo.insert(ctx_obj)
                    synced["glossary"] += 1
                except Exception as e:
                    print(f"Failed to sync glossary term {term.get('term')}: {e}")

        # Sync MDL
        if mdl:
            try:
                from app.modules.instruction.repositories import InstructionRepository
                from app.modules.instruction.models import Instruction

                mdl_repo = InstructionRepository(storage)
                mdl_content = mdl.get("content", "")
                mdl_obj = Instruction(
                    id=mdl.get("id", f"mdl-{connection_id}"),
                    condition="MDL",
                    rules=f"# Model Definition Language (MDL)\n{mdl_content}",
                    db_connection_id=connection_id,
                    is_default=False,
                )
                mdl_repo.insert(mdl_obj)
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
            if table.table_description:
                mdl_lines.append(f"**Description:** {table.table_description}")
            mdl_lines.append("")

            # Add columns
            mdl_lines.append("| Column | Type | Description |")
            mdl_lines.append("|--------|------|-------------|")

            if table.columns:
                for col in table.columns:
                    col_name = col.name
                    col_type = col.data_type
                    col_desc = col.description or ""
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

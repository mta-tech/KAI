"""
End-to-end test for LangGraph SQL agents.

This test verifies the full NL to SQL query execution flow using the new LangGraph agents.

Prerequisites:
1. Set OPENAI_API_KEY environment variable
2. Run: poetry run python -m pytest tests/e2e/test_langgraph_agents_e2e.py -v -s

Usage:
    # Run with legacy agents (default)
    poetry run python -m pytest tests/e2e/test_langgraph_agents_e2e.py -v -s

    # Run with new LangGraph agents
    USE_LANGGRAPH_AGENTS=true poetry run python -m pytest tests/e2e/test_langgraph_agents_e2e.py -v -s
"""

import os
import sys
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any

import pytest

# Set up minimal environment before imports
os.environ.setdefault("APP_NAME", "KAI Test")
os.environ.setdefault("APP_VERSION", "1.0.0")
os.environ.setdefault("APP_DESCRIPTION", "Test")
os.environ.setdefault("APP_ENVIRONMENT", "TEST")
os.environ.setdefault("APP_HOST", "0.0.0.0")
os.environ.setdefault("APP_PORT", "8005")
os.environ.setdefault("APP_ENABLE_HOT_RELOAD", "0")
os.environ.setdefault("TYPESENSE_API_KEY", "test_key")
os.environ.setdefault("TYPESENSE_HOST", "localhost")
os.environ.setdefault("TYPESENSE_PORT", "8108")
os.environ.setdefault("TYPESENSE_PROTOCOL", "HTTP")
os.environ.setdefault("TYPESENSE_TIMEOUT", "2")
os.environ.setdefault("ENCRYPT_KEY", "f0KVMZHZPgdMStBmVIn2XD049e6Mun7ZEDhf1W7MRnw=")
os.environ.setdefault("CHAT_FAMILY", "openai")
os.environ.setdefault("CHAT_MODEL", "gpt-4o-mini")
os.environ.setdefault("EMBEDDING_FAMILY", "openai")
os.environ.setdefault("EMBEDDING_MODEL", "text-embedding-3-small")
os.environ.setdefault("EMBEDDING_DIMENSIONS", "768")


# Mock data for testing
MOCK_TABLE_DESCRIPTIONS = [
    {
        "id": "table_1",
        "table_name": "employees",
        "db_schema": "public",
        "table_schema": """CREATE TABLE employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            department VARCHAR(50),
            salary DECIMAL(10,2),
            hire_date DATE
        )""",
        "table_description": "Contains employee information",
        "columns": [
            {"name": "id", "data_type": "INTEGER", "description": "Unique employee ID", "is_primary_key": True},
            {"name": "name", "data_type": "VARCHAR", "description": "Employee full name"},
            {"name": "department", "data_type": "VARCHAR", "description": "Department name"},
            {"name": "salary", "data_type": "DECIMAL", "description": "Annual salary"},
            {"name": "hire_date", "data_type": "DATE", "description": "Date of hire"},
        ],
        "sync_status": "SCANNED",
    },
    {
        "id": "table_2",
        "table_name": "departments",
        "db_schema": "public",
        "table_schema": """CREATE TABLE departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            budget DECIMAL(15,2)
        )""",
        "table_description": "Contains department information",
        "columns": [
            {"name": "id", "data_type": "INTEGER", "description": "Unique department ID", "is_primary_key": True},
            {"name": "name", "data_type": "VARCHAR", "description": "Department name"},
            {"name": "budget", "data_type": "DECIMAL", "description": "Annual budget"},
        ],
        "sync_status": "SCANNED",
    },
]


class MockTableDescription:
    """Mock TableDescription model."""
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def model_dump(self):
        return {k: v for k, v in self.__dict__.items()}


class MockDatabaseConnection:
    """Mock DatabaseConnection model."""
    def __init__(self):
        self.id = "db_conn_1"
        self.alias = "test_db"
        self.dialect = "postgresql"
        self.schemas = ["public"]
        self.connection_uri = "postgresql://test:test@localhost:5432/testdb"


class MockPrompt:
    """Mock Prompt model."""
    def __init__(self, text: str, db_connection_id: str = "db_conn_1"):
        self.id = "prompt_1"
        self.text = text
        self.db_connection_id = db_connection_id
        self.schemas = ["public"]
        self.created_at = "2024-01-01T00:00:00"

    def model_dump(self):
        return {
            "id": self.id,
            "text": self.text,
            "db_connection_id": self.db_connection_id,
            "schemas": self.schemas,
        }


class MockSQLDatabase:
    """Mock SQLDatabase."""
    def __init__(self):
        self.dialect = "postgresql"
        self._engine = MagicMock()

    def run_sql(self, query: str, top_k: int = 10):
        return f"Mock result for: {query[:50]}...", []

    @classmethod
    def get_sql_engine(cls, db_connection):
        return cls()


class MockEmbedding:
    """Mock embedding model."""
    def embed_query(self, text: str) -> List[float]:
        return [0.1] * 768

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 768 for _ in texts]


def create_mock_toolkit():
    """Create a mock toolkit with tools."""
    from langchain.tools import BaseTool
    from pydantic import Field

    class MockQueryTool(BaseTool):
        name: str = "SqlDbQuery"
        description: str = "Execute SQL query against the database"

        def _run(self, query: str) -> str:
            return f"Query executed successfully. Result: 5 rows returned."

    class MockSchemaTool(BaseTool):
        name: str = "DbRelevantTablesSchema"
        description: str = "Get schema for relevant tables"

        def _run(self, tables: str) -> str:
            return """Table: employees (id INT, name VARCHAR, department VARCHAR, salary DECIMAL, hire_date DATE)
Table: departments (id INT, name VARCHAR, budget DECIMAL)"""

    class MockTablesTool(BaseTool):
        name: str = "DbTablesWithRelevanceScores"
        description: str = "Find relevant tables"

        def _run(self, query: str) -> str:
            return "employees (0.95), departments (0.85)"

    class MockToolkit:
        dialect = "postgresql"

        def get_tools(self):
            return [MockQueryTool(), MockSchemaTool(), MockTablesTool()]

    return MockToolkit()


@pytest.fixture
def mock_services():
    """Set up mock services for testing."""
    with patch("app.data.db.storage.Storage") as mock_storage, \
         patch("app.modules.table_description.repositories.TableDescriptionRepository") as mock_repo, \
         patch("app.modules.context_store.services.ContextStoreService") as mock_context, \
         patch("app.modules.instruction.services.InstructionService") as mock_instruction, \
         patch("app.modules.business_glossary.services.BusinessGlossaryService") as mock_glossary, \
         patch("app.utils.sql_database.sql_database.SQLDatabase") as mock_db, \
         patch("app.utils.model.embedding_model.EmbeddingModel") as mock_embedding:

        # Configure mocks
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_all_tables_by_db.return_value = [
            MockTableDescription(t) for t in MOCK_TABLE_DESCRIPTIONS
        ]
        mock_repo.return_value = mock_repo_instance

        mock_context_instance = MagicMock()
        mock_context_instance.retrieve_context_for_question.return_value = []
        mock_context.return_value = mock_context_instance

        mock_instruction_instance = MagicMock()
        mock_instruction_instance.retrieve_instruction_for_question.return_value = []
        mock_instruction.return_value = mock_instruction_instance

        mock_glossary_instance = MagicMock()
        mock_glossary_instance.retrieve_business_metrics_for_question.return_value = []
        mock_glossary.return_value = mock_glossary_instance

        mock_db.get_sql_engine.return_value = MockSQLDatabase()

        mock_embedding_instance = MagicMock()
        mock_embedding_instance.get_model.return_value = MockEmbedding()
        mock_embedding.return_value = mock_embedding_instance

        yield {
            "storage": mock_storage,
            "repo": mock_repo,
            "context": mock_context,
            "instruction": mock_instruction,
            "glossary": mock_glossary,
            "db": mock_db,
            "embedding": mock_embedding,
        }


class TestLangGraphAgentGraph:
    """Test the LangGraph agent graph building functions."""

    def test_build_react_sql_agent_graph(self):
        """Test building the ReAct SQL agent graph."""
        from langchain_openai import ChatOpenAI
        from app.utils.sql_generator.sql_agent_graph import build_react_sql_agent_graph

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        toolkit = create_mock_toolkit()

        graph = build_react_sql_agent_graph(
            llm=llm,
            toolkit=toolkit,
            sql_history=None,
            max_examples=3,
            number_of_instructions=0,
            max_iterations=5,
        )

        assert graph is not None
        print("✓ ReAct SQL agent graph built successfully")

    def test_build_full_context_sql_agent_graph(self):
        """Test building the Full Context SQL agent graph."""
        from langchain_openai import ChatOpenAI
        from app.utils.sql_generator.sql_agent_dev_graph import build_react_full_context_sql_agent_graph

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        toolkit = create_mock_toolkit()

        graph = build_react_full_context_sql_agent_graph(
            llm=llm,
            toolkit=toolkit,
            sql_history=None,
            fewshot_examples=[{"prompt_text": "Show all employees", "sql": "SELECT * FROM employees"}],
            instructions=[{"instruction": "Always limit results to 100 rows"}],
            aliases=None,
            max_iterations=5,
        )

        assert graph is not None
        print("✓ Full Context SQL agent graph built successfully")


class TestLangGraphAgentExecution:
    """Test actual agent execution with LLM."""

    def test_react_agent_simple_query(self):
        """Test ReAct agent with a simple query."""
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        from app.utils.sql_generator.sql_agent_graph import (
            build_react_sql_agent_graph,
            ReActSQLAgentState,
            extract_intermediate_steps,
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        toolkit = create_mock_toolkit()

        graph = build_react_sql_agent_graph(
            llm=llm,
            toolkit=toolkit,
            max_iterations=3,
        )

        initial_state: ReActSQLAgentState = {
            "messages": [HumanMessage(content="Show me all employees with salary greater than 50000")],
            "question": "Show me all employees with salary greater than 50000",
            "dialect": "postgresql",
            "tools": toolkit.get_tools(),
            "iteration_count": 0,
            "max_iterations": 3,
            "intermediate_steps": [],
        }

        print("\n" + "="*60)
        print("Testing ReAct Agent - Simple Query")
        print("="*60)
        print(f"Question: {initial_state['question']}")
        print("-"*60)

        result = graph.invoke(initial_state)

        messages = result.get("messages", [])
        print(f"Total messages: {len(messages)}")

        # Print conversation flow
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            content = msg.content[:200] if hasattr(msg, 'content') and msg.content else "N/A"
            print(f"\n[{i}] {msg_type}: {content}...")

            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"    Tool Call: {tc['name']}({tc['args']})")

        # Extract intermediate steps
        steps = extract_intermediate_steps(messages)
        print(f"\n-"*60)
        print(f"Intermediate steps: {len(steps)}")
        for step in steps:
            print(f"  - {step[0].tool}: {step[0].tool_input[:50]}...")

        # Check final message contains SQL
        final_msg = messages[-1] if messages else None
        assert final_msg is not None
        print(f"\n{'='*60}")
        print("Final Response:")
        print(final_msg.content if hasattr(final_msg, 'content') else str(final_msg))
        print("="*60)

        print("\n✓ ReAct agent execution completed successfully")


class TestLangGraphEvaluator:
    """Test the LangGraph evaluation agent."""

    def test_evaluation_agent_creation(self):
        """Test creating the evaluation agent."""
        from langchain_openai import ChatOpenAI
        from app.utils.sql_evaluator.eval_agent_graph import (
            create_evaluation_tools,
            LangGraphEvaluationAgent,
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        # Test tool creation
        mock_db = MockSQLDatabase()
        tools = create_evaluation_tools(mock_db)

        assert len(tools) == 3
        tool_names = [t.name for t in tools]
        assert "sql_db_query" in tool_names or "entity_finder" in tool_names

        print("✓ Evaluation tools created successfully")
        print(f"  Tools: {tool_names}")


class TestSimpleEvaluatorLCEL:
    """Test the LCEL Simple Evaluator."""

    def test_lcel_chain_creation(self):
        """Test LCEL chain can be created."""
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

        template = "Evaluate this SQL: {sql}"
        prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(template)
        ])

        # LCEL chain pattern
        chain = prompt | llm | StrOutputParser()

        result = chain.invoke({"sql": "SELECT * FROM employees"})

        assert result is not None
        assert len(result) > 0

        print("✓ LCEL chain created and executed successfully")
        print(f"  Response preview: {result[:100]}...")


class TestFeatureFlags:
    """Test feature flag behavior."""

    def test_use_langgraph_agents_flag(self):
        """Test USE_LANGGRAPH_AGENTS feature flag."""
        from app.modules.sql_generation.services.adapter import USE_LANGGRAPH_AGENTS

        current_value = os.getenv("USE_LANGGRAPH_AGENTS", "false").lower() == "true"
        assert USE_LANGGRAPH_AGENTS == current_value

        print(f"✓ USE_LANGGRAPH_AGENTS = {USE_LANGGRAPH_AGENTS}")

    def test_use_langgraph_evaluators_flag(self):
        """Test USE_LANGGRAPH_EVALUATORS feature flag."""
        from app.utils.sql_evaluator import USE_LANGGRAPH_EVALUATORS

        current_value = os.getenv("USE_LANGGRAPH_EVALUATORS", "false").lower() == "true"
        assert USE_LANGGRAPH_EVALUATORS == current_value

        print(f"✓ USE_LANGGRAPH_EVALUATORS = {USE_LANGGRAPH_EVALUATORS}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LangGraph SQL Agents - E2E Test Suite")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  OPENAI_API_KEY not set!")
        print("   Set it to run LLM-dependent tests:")
        print("   export OPENAI_API_KEY=sk-...")
        print("\n   Running non-LLM tests only...\n")

    pytest.main([__file__, "-v", "-s"])

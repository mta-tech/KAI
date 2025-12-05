"""Unit tests for the Deep Agent adapter and proxy."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch


def stub_module(name: str, **attrs) -> types.ModuleType:
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


# Minimal stubs for external dependencies pulled in by adapter imports

@contextmanager
def _dummy_callback():
    class _Tracker:
        prompt_tokens = 0
        completion_tokens = 0
        total_cost = 0
        total_tokens = 0

    yield _Tracker()


stub_module("langchain_community.callbacks", get_openai_callback=_dummy_callback)
stub_module("langchain_core.tracers.langchain_v1", LangChainTracerV1=object)
stub_module("langchain.callbacks.manager", CallbackManagerForToolRun=object)
stub_module("langchain.callbacks.base", BaseCallbackManager=object)


def _dummy_agent_factory(*args, **kwargs):
    class _Agent:
        def invoke(self, payload):  # noqa: ARG002
            return {"messages": []}

        def stream(self, payload):  # noqa: ARG002
            if False:
                yield {}

    return _Agent()


agents_module = stub_module("app.agents", create_kai_sql_agent=_dummy_agent_factory)
agents_module.__path__ = []
stub_module(
    "app.agents.deep_agent_factory",
    DeepAgentRuntimeUnavailable=RuntimeError,
)
ToolSpec = type("ToolSpec", (), {})
stub_module("app.agents.types", ToolSpec=ToolSpec)
@dataclass
class _KaiToolContext:
    database: object
    db_scan: list
    embedding: object | None = None
    context: list | None = None
    few_shot_examples: list | None = None
    business_metrics: list | None = None
    aliases: list | None = None
    is_multiple_schema: bool = False
    top_k: int | None = None


def _build_tool_specs(ctx):  # noqa: ARG001
    return []


stub_module(
    "app.utils.deep_agent.tools",
    KaiToolContext=_KaiToolContext,
    build_tool_specs=_build_tool_specs,
)

lg_graph = stub_module(
    "langgraph.graph",
    Graph=object,
    START=object(),
    END=object(),
    MessagesState=object,
    StateGraph=object,
)
stub_module("langgraph.graph.graph", CompiledGraph=object)
stub_module("langgraph.prebuilt", ToolNode=object)
stub_module("langgraph.prebuilt.chat_agent_executor", create_react_agent=lambda *_, **__: None)

stub_module("langchain_ollama", ChatOllama=object, OllamaEmbeddings=object)
langchain_pkg = stub_module("langchain")
langchain_pkg.__path__ = []
langchain_agents = stub_module("langchain.agents")
langchain_agents.__path__ = []
stub_module("langchain.agents.agent", AgentExecutor=object)
langchain_chains = stub_module("langchain.chains")
langchain_chains.__path__ = []
stub_module("langchain.chains.llm", LLMChain=object)
stub_module("langchain.chains.base", Chain=object)
stub_module("langchain.schema", RUN_KEY="run_key", AgentAction=object)
stub_module("langchain.tools.base", BaseTool=object)
stub_module("langchain.chat_models.base", BaseChatModel=object)

class _Extra:
    forbid = "forbid"


stub_module(
    "langchain_core.pydantic_v1",
    BaseModel=object,
    Field=lambda *a, **k: None,
    SecretStr=str,
    root_validator=lambda *a, **k: (lambda fn: fn),
    validator=lambda *a, **k: (lambda fn: fn),
    Extra=_Extra,
)
prompts_module = stub_module(
    "langchain_core.prompts",
    PipelinePromptTemplate=object,
    ChatPromptTemplate=object,
    BasePromptTemplate=object,
    PromptTemplate=object,
    format_document=lambda *a, **k: "",
)
prompts_module.__path__ = []
stub_module("langchain_core.prompts.few_shot", FewShotPromptTemplate=object)
stub_module("langchain_core.prompts.prompt", PromptTemplate=object)
stub_module("langchain_core.prompts.chat", MessagesPlaceholder=object)

stub_module("langchain_openai", ChatOpenAI=object, OpenAIEmbeddings=object)
stub_module("langchain_openai.embeddings", AzureOpenAIEmbeddings=object, OpenAIEmbeddings=object)
stub_module("langchain_openai.embeddings.azure", AzureOpenAIEmbeddings=object)
stub_module("langchain_openai.embeddings.base", OpenAIEmbeddings=object)
stub_module("langchain_core.memory", BaseMemory=object)

stub_module(
    "langchain_google_genai",
    ChatGoogleGenerativeAI=object,
    GoogleGenerativeAIEmbeddings=object,
)
stub_module(
    "langchain_google_genai.embeddings",
    GoogleGenerativeAIEmbeddings=object,
)

stub_module("app.modules.nl_generation.services", NLGenerationService=object)
stub_module("app.utils.sql_evaluator.simple_evaluator", SimpleEvaluator=object)
stub_module("app.modules.context_store.services", ContextStoreService=object)
stub_module("app.modules.instruction.services", InstructionService=object)
stub_module("app.modules.business_glossary.services", BusinessGlossaryService=object)
class _StubSQLAgent:
    def __init__(self, llm_config=None, *_, **__):
        self.llm_config = llm_config


stub_module("app.utils.sql_generator.sql_agent", SQLAgent=_StubSQLAgent)
stub_module(
    "app.utils.sql_generator.sql_agent_dev",
    FullContextSQLAgent=type("FullContextSQLAgent", (), {}),
)
stub_module(
    "app.utils.sql_generator.graph_agent",
    LangGraphSQLAgent=type("LangGraphSQLAgent", (), {}),
)
class _DummyChatModel:
    def __init__(self, *_, **__):
        pass

    def get_model(self, *_, **__):
        return None


stub_module("app.utils.model.chat_model", ChatModel=_DummyChatModel)
class _DummySettings:
    def __init__(self, *_, **__):
        pass


stub_module("app.server.config", Settings=_DummySettings)


def load_adapter_module():
    adapter_path = Path(__file__).resolve().parents[2] / "app/modules/sql_generation/services/adapter.py"
    spec = importlib.util.spec_from_file_location("test_adapter_module", adapter_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter_module = load_adapter_module()
KaiSqlGeneratorAdapter = adapter_module.KaiSqlGeneratorAdapter
DeepAgentSQLGeneratorProxy = adapter_module.DeepAgentSQLGeneratorProxy

from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.utils.deep_agent.tools import KaiToolContext
from app.utils.sql_generator.sql_agent import SQLAgent


class DummyQueue:
    def __init__(self):
        self.items = []

    def put(self, value):
        self.items.append(value)


class AdapterSelectionTests(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.adapter = KaiSqlGeneratorAdapter(self.repo)
        self.llm_config = LLMConfig()
        self.db_connection = MagicMock(id="db1", dialect="postgresql")
        self.database = MagicMock()

    @patch.object(adapter_module, "DeepAgentSQLGeneratorProxy")
    def test_option_enables_deep_agent(self, proxy_cls):
        generator = self.adapter.select_generator(
            option="deep_agent",
            llm_config=self.llm_config,
            tenant_id="tenant",
            sql_generation_id="sg1",
            db_connection=self.db_connection,
            database=self.database,
            metadata={},
        )
        proxy_cls.assert_called_once()
        self.assertEqual(generator, proxy_cls.return_value)

    @patch.object(adapter_module, "DeepAgentSQLGeneratorProxy")
    def test_metadata_flag_enables_deep_agent(self, proxy_cls):
        generator = self.adapter.select_generator(
            option="",
            llm_config=self.llm_config,
            tenant_id="tenant",
            sql_generation_id="sg1",
            db_connection=self.db_connection,
            database=self.database,
            metadata={"use_deep_agent": True},
        )
        proxy_cls.assert_called_once()
        self.assertEqual(generator, proxy_cls.return_value)

    def test_default_returns_sqlagent(self):
        generator = self.adapter.select_generator(
            option="",
            llm_config=self.llm_config,
            tenant_id="tenant",
            sql_generation_id="sg1",
            db_connection=self.db_connection,
            database=self.database,
            metadata={},
        )
        self.assertIsInstance(generator, SQLAgent)


class DeepAgentProxyTests(unittest.TestCase):
    def setUp(self):
        self.db_connection = MagicMock(id="db1", dialect="postgresql")
        self.database = MagicMock()
        self.tool_context = KaiToolContext(
            database=self.database,
            db_scan=[],
        )
        self.proxy = DeepAgentSQLGeneratorProxy(
            LLMConfig(),
            tenant_id="tenant",
            sql_generation_id="sg1",
            db_connection=self.db_connection,
            database=self.database,
            tool_context=self.tool_context,
            extra_instructions=[],
        )
        self.user_prompt = MagicMock(id="prompt1", text="select", schemas=[])
        self.queue = DummyQueue()

    def _fake_agent(self):
        class Agent:
            def stream(self, payload):  # noqa: ARG002
                yield {
                    "todos": [{"status": "pending", "text": "Plan"}],
                    "tool": {"name": "sql_db_query", "output": "rows"},
                    "messages": [{"content": "thinking"}],
                    "output": "SELECT 1",
                    "files": ["/tmp/result.csv"],
                }

            def invoke(self, payload):  # noqa: ARG002
                return {"messages": [{"content": "SELECT 1"}]}

        return Agent()

    @patch.object(adapter_module, "create_kai_sql_agent")
    def test_stream_response_records_artifacts(self, agent_factory):
        agent_factory.return_value = self._fake_agent()
        with patch.object(
            DeepAgentSQLGeneratorProxy,
            "create_sql_query_status",
            side_effect=lambda db, query, sql_generation: sql_generation,
        ):
            response = SQLGeneration(
                prompt_id="prompt1",
                llm_config=LLMConfig(),
                metadata={},
            )
            result = self.proxy.stream_response(
                user_prompt=self.user_prompt,
                database_connection=self.db_connection,
                response=response,
                queue=self.queue,
                metadata={},
            )

        runtime_details = result.metadata.get("runtime_details")
        self.assertIsNotNone(runtime_details)
        artifacts = runtime_details.get("artifacts")
        self.assertTrue(any(a.get("type") == "todos" for a in artifacts))
        self.assertTrue(any(a.get("type") == "files" for a in artifacts))
        self.assertTrue(any("Plan Update" in entry for entry in self.queue.items))


if __name__ == "__main__":
    unittest.main()

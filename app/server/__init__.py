import fastapi
from app.api import API

from app.data.db.storage import Storage
from app.server.config import Settings
from app.utils.sql_database.sql_database import DBConnections

# Session module imports
from app.modules.session import (
    router as session_router,
    set_session_service,
    SessionService,
    SessionRepository,
    TypesenseCheckpointer,
    build_session_graph,
)

# Autonomous agent session imports
from app.modules.autonomous_agent import (
    agent_session_router,
    set_agent_session_storage,
)

# Visualization module imports
from app.modules.visualization import visualization_router

# Analytics module imports
from app.modules.analytics import analytics_router

# API v2 imports
from app.api.v2 import batch_router, streaming_router

from app.modules.sql_generation.services import SQLGenerationService
from app.modules.analysis.services import AnalysisService

import logging

logger = logging.getLogger(__name__)


class FastAPI:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._storage = Storage(settings)
        self._app = fastapi.FastAPI(
            debug=True,
            title=settings.APP_NAME,
            description=settings.APP_DESCRIPTION,
            version=settings.APP_VERSION,
        )

        self._api = API(self._storage)
        self._app.include_router(self._api.get_router())

        # Configure and register session module
        self._setup_session_module()

        # Configure and register autonomous agent session module
        self._setup_agent_session_module()

        # Configure and register analysis suggestions module
        self._setup_suggestions_module()

        # Configure and register dashboard module
        self._setup_dashboard_module()

        @self._app.on_event("shutdown")
        async def shutdown_event():
            DBConnections.dispose_all_engines()

    def _setup_session_module(self):
        """Configure and register the session module."""
        # Create dependencies
        repository = SessionRepository(self._storage)
        checkpointer = TypesenseCheckpointer(self._storage)

        # Get existing services
        sql_generation_service = SQLGenerationService(self._storage)
        analysis_service = AnalysisService(self._storage)

        # Get LLM for summarization with fallback support
        llm = self._get_session_llm()

        # Build graph
        graph = build_session_graph(
            sql_generation_service=sql_generation_service,
            analysis_service=analysis_service,
            llm=llm,
            checkpointer=checkpointer
        )

        # Create and configure service
        service = SessionService(repository, graph, checkpointer)
        set_session_service(service)

        # Include session router
        self._app.include_router(session_router, prefix="/api/v1", tags=["Sessions"])

    def _get_session_llm(self):
        """Get LLM for session summarization with fallback support.

        Priority:
        1. Google Gemini (if GOOGLE_API_KEY is set)
        2. Configured CHAT_FAMILY/CHAT_MODEL from settings
        3. OpenAI gpt-4o-mini (if OPENAI_API_KEY is set)

        Raises ValueError if no LLM can be configured.
        """
        # Try Google Gemini first
        if self._settings.GOOGLE_API_KEY:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("Session LLM: Using Google Gemini for summarization")
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=self._settings.GOOGLE_API_KEY
            )

        # Fall back to configured chat model
        chat_family = self._settings.CHAT_FAMILY
        chat_model = self._settings.CHAT_MODEL

        if chat_family and chat_model:
            logger.info(f"Session LLM: Using configured {chat_family}/{chat_model} for summarization")
            from app.utils.model.chat_model import ChatModel
            return ChatModel().get_model(
                database_connection=None,
                model_family=chat_family,
                model_name=chat_model,
            )

        # Fall back to OpenAI
        if self._settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            logger.info("Session LLM: Using OpenAI gpt-4o-mini for summarization")
            return ChatOpenAI(
                model_name="gpt-4o-mini",
                openai_api_key=self._settings.OPENAI_API_KEY,
            )

        raise ValueError(
            "No LLM configured for session summarization. "
            "Please set one of: GOOGLE_API_KEY, CHAT_FAMILY+CHAT_MODEL, or OPENAI_API_KEY"
        )

    def _setup_agent_session_module(self):
        """Configure and register the autonomous agent session module."""
        # Set storage for agent session repository
        set_agent_session_storage(self._storage)

        # Include agent session router
        self._app.include_router(
            agent_session_router, prefix="/api/v1", tags=["Agent Sessions"]
        )

        # Include visualization router (v2 API)
        self._app.include_router(visualization_router)

        # Include analytics router (v2 API)
        self._app.include_router(analytics_router)

        # Include streaming router (v2 API)
        self._app.include_router(streaming_router)

        # Include batch router (v2 API)
        self._app.include_router(batch_router)

    def _setup_suggestions_module(self):
        """Configure and register the analysis suggestions module."""
        from app.modules.analysis_suggestions.api import create_suggestions_router
        from app.modules.analysis_suggestions.services import AnalysisSuggestionService

        service = AnalysisSuggestionService(self._storage)
        suggestions_router = create_suggestions_router(service)
        self._app.include_router(suggestions_router)

    def _setup_dashboard_module(self):
        """Configure and register the dashboard module."""
        from app.modules.dashboard.api import create_dashboard_router
        from app.modules.dashboard.services import DashboardService

        service = DashboardService(self._storage)
        dashboard_router = create_dashboard_router(service)
        self._app.include_router(dashboard_router)

    def app(self) -> fastapi.FastAPI:
        return self._app

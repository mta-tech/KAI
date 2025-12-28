import fastapi
from fastapi.middleware.cors import CORSMiddleware
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
from app.modules.sql_generation.services import SQLGenerationService
from app.modules.analysis.services import AnalysisService
from langchain_google_genai import ChatGoogleGenerativeAI


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

        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._api = API(self._storage)
        self._app.include_router(self._api.get_router())

        # Configure and register session module
        self._setup_session_module()

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

        # Get LLM for summarization (using Gemini)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", google_api_key=self._settings.GOOGLE_API_KEY
        )

        # Build graph
        graph = build_session_graph(
            sql_generation_service=sql_generation_service,
            analysis_service=analysis_service,
            llm=llm,
            checkpointer=checkpointer,
        )

        # Create and configure service
        service = SessionService(repository, graph, checkpointer)
        set_session_service(service)

        # Include session router
        self._app.include_router(session_router, prefix="/api/v1", tags=["Sessions"])

    def app(self) -> fastapi.FastAPI:
        return self._app

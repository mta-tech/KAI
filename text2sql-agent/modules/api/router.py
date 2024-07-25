from http import client
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .handler import connector_handler, table_status_handler, table_scanner_handler, conversation_handler
from .handler import es_add_sql_handler, es_search_sql_handler, es_update_sql_handler, es_delete_sql_handler

from modules.lib.exception import MTACommonError, MTAErrorException


class ApiText2SqlServiceRouter:
    def create_router(self):
        router = FastAPI()

        self.build_router(router)
        self.handler_error_exception(router)

        return router

    @staticmethod
    def build_router(router: FastAPI):
        connh = connector_handler
        tstat = table_status_handler
        tscan = table_scanner_handler
        ch = conversation_handler

        router.include_router(connh, prefix="/connectors", tags=["connectors"])
        router.include_router(tstat, prefix="/table-status", tags=["table-status"])
        router.include_router(tscan, prefix="/table-scanner", tags=["table-scanner"])
        router.include_router(ch, prefix="/conversations", tags=["conversations"])

        router.include_router(es_add_sql_handler, prefix="/add-golden-sql", tags=["add-golden-sql"])
        router.include_router(es_search_sql_handler, prefix="/search-golden-sql", tags=["search-golden-sql"])
        router.include_router(es_update_sql_handler, prefix="/update-golden-sql", tags=["update-golden-sql"])
        router.include_router(es_delete_sql_handler, prefix="/delete-golden-sql", tags=["delete-golden-sql"])


    @staticmethod
    def handler_error_exception(router: FastAPI):
        # Middleware untuk menangani error dari sistem
        @router.exception_handler(Exception)
        async def handle_exception(_, exc):
            err = MTAErrorException(MTACommonError())
            err.set_system_message(str(exc))

            return JSONResponse(
                status_code=client.INTERNAL_SERVER_ERROR,
                content=err.detail,
            )

        # Middleware untuk menangani custom error dari sistem
        @router.exception_handler(MTAErrorException)
        async def handle_common_exception(_, exc: MTAErrorException):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)

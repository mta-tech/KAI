from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from modules.lib.dataherald_connector import connector as connector_module
from modules.lib.dataherald_table_status import table_status as table_status_module
from modules.lib.dataherald_table_scanner import table_scanner as table_scanner_module
from modules.lib.dataherald_conversation import conversation as conversation_module

from modules.lib.elasticsearch_client import add_sql_production as add_sql_module
from modules.lib.elasticsearch_client import search_sql as search_sql_module
from modules.lib.elasticsearch_client import update_sql as update_sql_module
from modules.lib.elasticsearch_client import delete_sql as delete_sql_module


from modules.lib.exception import MTAErrorException
from errors.error import ERROR_CONVERSATIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ Database Connector ============

connector_handler = APIRouter()

class ConnectorDTO(BaseModel):
    thread_id: Optional[str] = None
    db_type: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_schemas: List[str]

@connector_handler.post("")
def init_connector(body: ConnectorDTO) -> Dict[str, Any]:
    try:
        db_connection_id, table_info = connector_module(
            body.db_type, body.db_user, body.db_password, body.db_host, body.db_port, body.db_name, body.db_schemas
        )
        content = {
            "db_connection_id": db_connection_id,
            "table_info": table_info
        }
        return {"thread_id": body.thread_id, "content": content}
    except Exception as e:
        logger.error(f"Error initializing database connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Table Status ============

table_status_handler = APIRouter()

class TableStatusDTO(BaseModel):
    thread_id: Optional[str] = None
    db_connection_id: str

@table_status_handler.post("")
def init_table_status(body: TableStatusDTO) -> Dict[str, Any]:
    try:
        db_connection_id, table_info = table_status_module(body.db_connection_id)
        content = {
            "db_connection_id": db_connection_id,
            "table_info": table_info
        }
        return {"thread_id": body.thread_id, "content": content}
    except Exception as e:
        logger.error(f"Error retrieving table status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Table Scanner ============

table_scanner_handler = APIRouter()

class TableScannerDTO(BaseModel):
    thread_id: Optional[str] = None
    table_ids: List[str]

@table_scanner_handler.post("")
def init_table_scanner(body: TableScannerDTO) -> Dict[str, Any]:
    try:
        db_connection_id, table_info = table_scanner_module(body.table_ids)
        content = {
            "db_connection_id": db_connection_id,
            "table_info": table_info
        }
        return {"thread_id": body.thread_id, "content": content}
    except Exception as e:
        logger.error(f"Error scanning tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Conversation ============

conversation_handler = APIRouter()

class ConversationDTO(BaseModel):
    thread_id: Optional[str] = None
    prompt: str
    db_connection_id: str

@conversation_handler.post("")
def conversation(body: ConversationDTO) -> Dict[str, Any]:
    try:
        sql_generation, sql_generation_status, sql_execution = conversation_module(body.db_connection_id, body.prompt)
        content = {
            "sql_generation": sql_generation,
            "sql_generation_status": sql_generation_status,
            "sql_execution": sql_execution,
        }
        return {"thread_id": body.thread_id, "content": content}
    except Exception as e:
        logger.error(f"Error during conversation process: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ============ ES ADD SQL ============

es_add_sql_handler = APIRouter()

class EsAddSQLDTO(BaseModel):
    thread_id: Optional[str] = None
    index_name: str 
    question: str
    sql_query: str
    use_keyword: int


@es_add_sql_handler.post("")
def es_add_sql(body: EsAddSQLDTO) -> Dict[str, Any]:
    print("test")
    try:
        message = add_sql_module(body.index_name, body.question, body.sql_query, body.use_keyword)
        return {"thread_id": body.thread_id, "content": message}
    except Exception as e:
        logger.error(f"Error during add sql process: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ============ ES SEARCH SQL ============

es_search_sql_handler = APIRouter()

class EsSearchSQLDTO(BaseModel):
    thread_id: Optional[str] = None
    index_name: str 
    query: str
    use_keyword: int


@es_search_sql_handler.post("")
def es_add_sql(body: EsSearchSQLDTO) -> Dict[str, Any]:
    try:
        document = search_sql_module(body.index_name, body.query, body.use_keyword)
        return {"thread_id": body.thread_id, "content": document}
    except Exception as e:
        logger.error(f"Error during add sql process: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ES UPDATE SQL ============

es_update_sql_handler = APIRouter()

class EsUpdateSQLDTO(BaseModel):
    thread_id: Optional[str] = None
    index_name: str 
    doc_id: str 
    question: str
    sql_query: str
    use_keyword: int

@es_update_sql_handler.post("")
def es_add_sql(body: EsUpdateSQLDTO) -> Dict[str, Any]:
    try:
        message = update_sql_module(body.index_name, body.doc_id, body.question, body.sql_query, body.use_keyword)
        return {"thread_id": body.thread_id, "content": message}
    except Exception as e:
        logger.error(f"Error during update sql process: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ES DELETE SQL ============

es_delete_sql_handler = APIRouter()

class EsDeleteSQLDTO(BaseModel):
    thread_id: Optional[str] = None
    index_name: str 
    doc_id: str


@es_delete_sql_handler.post("")
def es_add_sql(body: EsDeleteSQLDTO) -> Dict[str, Any]:
    try:
        message = delete_sql_module(body.index_name, body.doc_id)
        return {"thread_id": body.thread_id, "content": message}
    except Exception as e:
        logger.error(f"Error during delete sql process: {e}")
        raise HTTPException(status_code=500, detail=str(e))
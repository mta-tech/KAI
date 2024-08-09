from app.storage.schemas.column_description import ColumnDescriptionSchema
from app.storage.schemas.context_store import ContextStoreSchema
from app.storage.schemas.database_connection import DatabaseConnectionSchema
from app.storage.schemas.database_instruction import DatabaseInstructionSchema
from app.storage.schemas.nl_generation import NLGenerationSchema
from app.storage.schemas.prompt import PromptSchema
from app.storage.schemas.sql_generation import SQLGenerationSchema
from app.storage.schemas.table_description import TableDescriptionSchema

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SchemaInitialization:
    @staticmethod
    def initialize():
        DatabaseConnectionSchema()
        logging.info("DatabaseConnectionSchema initialized successfully")
        DatabaseInstructionSchema()
        logging.info("DatabaseInstructionSchema initialized successfully")
        ContextStoreSchema()
        logging.info("ContextStoreSchema initialized successfully")
        PromptSchema()
        logging.info("PromptSchema initialized successfully")
        SQLGenerationSchema()
        logging.info("SQLGenerationSchema initialized successfully")
        NLGenerationSchema()
        logging.info("NLGenerationSchema initialized successfully")
        TableDescriptionSchema()
        logging.info("TableDescriptionSchema initialized successfully")
        ColumnDescriptionSchema()
        logging.info("ColumnDescriptionSchema initialized successfully")

import logging
import os

from app.data.typesense.schemas.column_description import ColumnDescriptionSchema
from app.data.typesense.schemas.context_store import ContextStoreSchema
from app.data.typesense.schemas.database_connection import DatabaseConnectionSchema
from app.data.typesense.schemas.database_instruction import DatabaseInstructionSchema
from app.data.typesense.schemas.nl_generation import NLGenerationSchema
from app.data.typesense.schemas.prompt import PromptSchema
from app.data.typesense.schemas.sql_generation import SQLGenerationSchema
from app.data.typesense.schemas.table_description import TableDescriptionSchema

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

FLAG_FILE = "initialized.flag"


class SchemaInitialization:
    def initialize_database(self):
        if not os.path.exists(FLAG_FILE):
            SchemaInitialization.initialize()
            with open(FLAG_FILE, "w") as file:
                file.write("Database initialized")

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

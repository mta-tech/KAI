from app.utils.sql_database.sql_database import SQLDatabase
from app.modules.sql_generation.models import SQLGeneration
from app.server.config import Settings
from app.utils.core.timeout import run_with_timeout


def format_error_message(
    sql_generation: SQLGeneration, error_message: str
) -> SQLGeneration:
    # Remove the complete query
    if error_message.find("[") > 0 and error_message.find("]") > 0:
        error_message = (
            error_message[0 : error_message.find("[")]
            + error_message[error_message.rfind("]") + 1 :]
        )
    sql_generation.status = "INVALID"
    sql_generation.error = error_message
    return sql_generation


def create_sql_query_status(
    db: SQLDatabase,
    query: str,
    sql_generation: SQLGeneration,
) -> SQLGeneration:
    """Find the sql query status and populate the fields sql_query_result, sql_generation_status, and error_message"""
    if query == "":
        sql_generation.status = "INVALID"
        sql_generation.error = "Sorry, we couldn't generate an SQL from your prompt"
    else:
        try:
            settings = Settings()
            query = db.parser_to_filter_commands(query)
            run_with_timeout(
                db.run_sql,
                args=(query,),
                timeout_duration=settings.SQL_EXECUTION_TIMEOUT,
            )
            sql_generation.status = "VALID"
            sql_generation.error = None
        except TimeoutError:
            sql_generation = format_error_message(
                sql_generation,
                "The query execution exceeded the timeout.",
            )
        except Exception as e:
            sql_generation = format_error_message(sql_generation, str(e))
    return sql_generation

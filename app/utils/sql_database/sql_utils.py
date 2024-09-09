from sql_metadata import Parser

from app.modules.context_store.models import ContextStore


def extract_the_schemas_from_sql(sql: str) -> list[str]:
    table_names = Parser(sql).tables
    schemas = []
    for table_name in table_names:
        if "." in table_name:
            schema = table_name.split(".")[0]
            schemas.append(schema.strip())
    return schemas


def filter_golden_records_based_on_schema(
    context_stores: list[ContextStore], schemas: list[str]
) -> list[ContextStore]:
    filtered_records = []
    if not schemas:
        return context_stores
    for record in context_stores:
        used_schemas = extract_the_schemas_from_sql(record.sql)
        for schema in schemas:
            if schema in used_schemas:
                filtered_records.append(record)
                break
    return filtered_records

from app.modules.table_description.models import TableDescription
from app.modules.context_store.models import ContextStore

from typing import List

def simplify_table_description(table_desc: TableDescription) -> dict:
    """
    Simplify a TableDescription object for LLM prompts by removing unnecessary information.

    Args:
        table_desc: The TableDescription object to simplify

    Returns:
        A simplified dictionary with only the essential information
    """
    # Extract only the essential column information
    simplified_columns = []
    for col in table_desc.columns:
        simplified_col = {
            "name": col.name,
            "description": col.description,
            "data_type": col.data_type,
        }
        # Only include categories if they exist and the column has low cardinality
        if col.low_cardinality and col.categories:
            # Limit the number of categories to display
            if len(col.categories) > 5:
                simplified_col["categories"] = col.categories[:5] + ["..."]
            else:
                simplified_col["categories"] = col.categories
        simplified_columns.append(simplified_col)

    # Create a simplified table description
    simplified_table = {
        "name": table_desc.table_name,
        "schema": table_desc.db_schema,
        "description": table_desc.table_description,
        "columns": simplified_columns,
        # Include a small number of examples if available
        "examples": table_desc.examples[:2] if table_desc.examples else [],
    }

    return simplified_table


def format_table_descriptions_for_prompt(
    table_descriptions: list[TableDescription],
    relevant_tables: list = None,
    relevant_columns: list[str] = None,
) -> str:
    """
    Format a list of TableDescription objects into a string suitable for LLM prompts.

    Args:
        table_descriptions: List of TableDescription objects

    Returns:
        A formatted string representation of the table descriptions
    """
    formatted_str = ""

    for table_desc in table_descriptions:
        simplified = simplify_table_description(table_desc)
        
        if relevant_tables and simplified['name'] not in relevant_tables:
            continue

        formatted_str += f"Table: {simplified['name']}\n"
        formatted_str += f"Schema: {simplified['schema']}\n"
        if simplified["description"]:
            formatted_str += f"Description: {simplified['description']}\n"

        formatted_str += "Columns:\n"
        for col in simplified["columns"]:
            col_str = f"  - {col['name']} ({col['data_type']})"
            if col["description"]:
                col_str += f": {col['description']}"
            if "categories" in col:
                col_str += f" [Values: {', '.join(str(c) for c in col['categories'])}]"
            formatted_str += col_str + "\n"

        if simplified["examples"]:
            formatted_str += "Examples:\n"
            for example in simplified["examples"]:
                formatted_str += f"  {example}\n"

        formatted_str += "\n"

    return formatted_str


def build_base_prompt(table_descriptions: str, num_questions: int) -> str:
    return f"""Generate {num_questions} number of relevant intents based on the following context:

    ## Table Descriptions
    {table_descriptions}
    """

def add_user_instruction(prompt: str, user_instruction: str) -> str:
    if user_instruction and len(user_instruction.strip()) > 10:
        prompt += f"\n## High Priority Instruction\n{user_instruction.strip()}\n"
        if "intent" not in user_instruction.lower():
            prompt += "\nYou can use the Table Descriptions to inspire intent generation if helpful.\n"
    return prompt

def get_default_instruction_block(db_intent) -> str:
    return f"""
    ## Instructions
    1. Format each intent as a single line, with the level of detail needed.

    ## Intents Example
    {db_intent}
    """

def get_context_store_block(context_stores: List[ContextStore]) -> str:
    if not context_stores:
        return ""
    
    context_block = """
    ## Instructions
    1. Based on the provided Context Stores, generate new intents that are different from the ones explicitly stated.
    2. Use the Context Stores as inspiration or additional context only.
    3. Each intent should be written in a single line with the necessary level of detail.
    4. Do not repeat or rephrase the intents already mentioned in the Context Stores.

    ## Context Stores
    """
    for context in context_stores:
        context_block += f"- '{context.prompt_text}'\n"
    return context_block

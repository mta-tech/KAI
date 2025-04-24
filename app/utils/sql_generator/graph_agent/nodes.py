from typing import List
from datetime import datetime
import logging
import numpy as np

from app.data.db.storage import Storage
from app.modules.business_glossary.services import BusinessGlossaryService
from app.modules.context_store.services import ContextStoreService
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.modules.instruction.services import InstructionService
from app.modules.prompt.models import Prompt
from app.modules.table_description.models import TableDescriptionStatus
from app.modules.table_description.repositories import TableDescriptionRepository
from app.server.config import Settings
from app.utils.model.embedding_model import EmbeddingModel
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.sql_tools import replace_unprocessable_characters
from app.utils.sql_generator.graph_agent.state import SQLAgentState

logger = logging.getLogger(__name__)

# Context Collection Nodes


def collect_context(state: SQLAgentState) -> SQLAgentState:
    """Collect context from various services.

    This node is responsible for:
    1. Retrieving the database connection
    2. Getting table descriptions (db_scan)
    3. Retrieving few-shot examples relevant to the question
    4. Retrieving instructions relevant to the question
    5. Retrieving business metrics relevant to the question
    6. Retrieving aliases if provided in metadata

    Args:
        state: The current state of the SQL agent

    Returns:
        Updated state with collected context
    """
    try:
        logger.info(f"Collecting context for question: {state.question}")

        # Initialize services
        storage = Storage(Settings())
        context_store_service = ContextStoreService(storage)
        instruction_service = InstructionService(storage)
        business_metrics_service = BusinessGlossaryService(storage)
        repository = TableDescriptionRepository(storage)
        db_connection_repository = DatabaseConnectionRepository(storage)

        # Get database connection
        db_connection = db_connection_repository.find_by_id(state.db_connection_id)
        if not db_connection:
            state.error = (
                f"Database connection with ID {state.db_connection_id} not found"
            )
            state.status = "INVALID"
            return state

        # Create a prompt object from the question
        # This is needed because the services expect a Prompt object
        prompt = Prompt(
            id=state.prompt_id,
            text=state.question,
            schemas=db_connection.schemas if hasattr(db_connection, "schemas") else [],
            created_at=state.created_at,
        )

        # Get table descriptions (db_scan)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": state.db_connection_id,
                "sync_status": TableDescriptionStatus.SCANNED.value,
            }
        )

        if not db_scan:
            state.error = "No scanned tables found for database"
            state.status = "INVALID"
            return state

        # Filter tables by schema if specified in the prompt
        if hasattr(prompt, "schemas") and prompt.schemas:
            db_scan = SQLGenerator.filter_tables_by_schema(
                db_scan=db_scan, prompt=prompt
            )

        # Get few-shot examples
        few_shot_examples = context_store_service.retrieve_context_for_question(prompt)

        # Get instructions
        instructions = instruction_service.retrieve_instruction_for_question(prompt)

        # Get business metrics
        business_metrics = (
            business_metrics_service.retrieve_business_metrics_for_question(prompt)
        )

        # Get aliases from metadata if available
        aliases = state.metadata.get("aliases") if state.metadata else None

        # Update state with collected context
        state.db_scan = [table.model_dump() for table in db_scan]

        if few_shot_examples:
            # Remove duplicates
            state.few_shot_examples = remove_duplicate_examples(few_shot_examples)

        if instructions:
            state.instructions = instructions

        if business_metrics:
            state.business_metrics = business_metrics

        if aliases:
            state.aliases = aliases

        logger.info(
            f"Context collection complete. Found {len(state.db_scan)} tables, "
            f"{len(state.few_shot_examples) if state.few_shot_examples else 0} examples, "
            f"{len(state.instructions) if state.instructions else 0} instructions, "
            f"{len(state.business_metrics) if state.business_metrics else 0} business metrics, "
            f"{len(state.aliases) if state.aliases else 0} aliases."
        )

        return state
    except Exception as e:
        logger.error(f"Error collecting context: {str(e)}")
        state.error = f"Error collecting context: {str(e)}"
        state.status = "INVALID"
        return state


def remove_duplicate_examples(examples: List[dict]) -> List[dict]:
    """Remove duplicate examples based on prompt_text.

    Args:
        examples: List of example dictionaries

    Returns:
        List of examples with duplicates removed
    """
    returned_result = []
    seen_list = []
    for example in examples:
        if example["prompt_text"] not in seen_list:
            seen_list.append(example["prompt_text"])
            returned_result.append(example)
    return returned_result


# Table Identification Node


def identify_relevant_tables(state: SQLAgentState) -> SQLAgentState:
    """Identify tables that are relevant to the user's question using embedding similarity.

    This node is responsible for:
    1. Creating embeddings for the user's question
    2. Creating embeddings for table representations
    3. Calculating similarity scores between the question and tables
    4. Selecting the most relevant tables
    5. Including tables from few-shot examples if available

    Args:
        state: The current state of the SQL agent

    Returns:
        Updated state with relevant tables
    """
    try:
        logger.info(f"Identifying relevant tables for question: {state.question}")

        if not state.db_scan:
            logger.warning("No tables available in db_scan")
            return state

        # Get embedding model
        embedding_model = EmbeddingModel().get_model()

        # Get question embedding
        question_embedding = embedding_model.embed_query(
            state.question.replace("\n", " ")
        )

        # Create table representations and calculate similarity
        table_representations = []
        for table in state.db_scan:
            # Create column representation
            col_rep = ""
            for column in table.get("columns", []):
                if column.get("description"):
                    col_rep += f"{column['name']}: {column['description']}, "
                else:
                    col_rep += f"{column['name']}, "

            # Create table representation
            if table.get("table_description"):
                table_rep = f"Table {table['table_name']} contain columns: [{col_rep}], this tables has: {table['table_description']}"
            else:
                table_rep = f"Table {table['table_name']} contain columns: [{col_rep}]"

            # Add to list
            table_representations.append(
                {
                    "db_schema": table.get("db_schema"),
                    "table_name": table.get("table_name"),
                    "representation": table_rep,
                }
            )

        # Calculate similarities
        for table in table_representations:
            table_embedding = embedding_model.embed_query(table["representation"])
            similarity = cosine_similarity(question_embedding, table_embedding)
            table["similarity"] = similarity

        # Sort by similarity
        table_representations.sort(key=lambda x: x["similarity"], reverse=True)

        # Get tables from few-shot examples
        few_shot_tables = []
        if state.few_shot_examples:
            try:
                from sql_metadata import Parser

                for example in state.few_shot_examples:
                    if "sql" in example:
                        try:
                            tables = Parser(example["sql"]).tables
                            for table_name in tables:
                                # Find matching tables in db_scan
                                for table in state.db_scan:
                                    if table["table_name"] == table_name:
                                        few_shot_tables.append(
                                            {
                                                "db_schema": table.get("db_schema"),
                                                "table_name": table["table_name"],
                                                "similarity": 1.0,  # High similarity since it's from examples
                                                "from_few_shot": True,
                                            }
                                        )
                        except Exception as e:
                            logger.error(
                                f"Error parsing SQL in few-shot example: {str(e)}"
                            )
            except ImportError:
                logger.warning(
                    "sql_metadata not available, skipping few-shot table extraction"
                )

        # Combine and deduplicate
        seen_tables = set()
        combined_tables = []

        # Add few-shot tables first
        for table in few_shot_tables:
            table_key = (
                f"{table['db_schema']}.{table['table_name']}"
                if table.get("db_schema")
                else table["table_name"]
            )
            if table_key not in seen_tables:
                seen_tables.add(table_key)
                combined_tables.append(table)

        # Add similarity-based tables
        top_k = 20  # Limit to top 20 tables
        for table in table_representations[:top_k]:
            table_key = (
                f"{table['db_schema']}.{table['table_name']}"
                if table.get("db_schema")
                else table["table_name"]
            )
            if table_key not in seen_tables:
                seen_tables.add(table_key)
                combined_tables.append(table)

        # Update state
        state.relevant_tables = combined_tables

        # Log results
        table_names = [
            f"{t.get('db_schema', '')}.{t['table_name']}"
            if t.get("db_schema")
            else t["table_name"]
            for t in combined_tables
        ]
        logger.info(
            f"Identified {len(state.relevant_tables)} relevant tables: {', '.join(table_names)}"
        )

        return state
    except Exception as e:
        logger.error(f"Error identifying relevant tables: {str(e)}")
        # Don't set error state here, as this is not a critical failure
        # We can continue with an empty list of relevant tables if needed
        state.relevant_tables = []
        return state


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        a: First vector
        b: Second vector

    Returns:
        Cosine similarity score
    """
    if not a or not b:  # Check for empty vectors
        return 0.0

    if len(a) != len(b):  # Ensure both vectors have the same length
        raise ValueError("Vector embeddings must have the same length")

    if (np.linalg.norm(a) == 0) or (np.linalg.norm(b) == 0):  # Handle zero vectors
        return 0.0

    return round(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), 4)


# Schema Analysis Node


def analyze_schemas(state: SQLAgentState) -> SQLAgentState:
    """Analyze schemas of relevant tables.

    This node is responsible for:
    1. Extracting table names from the relevant_tables list
    2. Retrieving schema information for those tables from db_scan
    3. Formatting the schema information in a structured way

    Args:
        state: The current state of the SQL agent

    Returns:
        Updated state with table schemas
    """
    try:
        logger.info("Analyzing schemas for relevant tables")

        if not state.relevant_tables:
            logger.warning("No relevant tables to analyze schemas for")
            return state

        # Extract table names from relevant_tables
        relevant_table_names = []
        for table in state.relevant_tables:
            if table.get("db_schema"):
                relevant_table_names.append((table["db_schema"], table["table_name"]))
            else:
                relevant_table_names.append((None, table["table_name"]))

        # Get schema information for relevant tables
        schemas = {}
        for db_schema, table_name in relevant_table_names:
            # Find the table in db_scan
            for table in state.db_scan:
                if (
                    table["table_name"] == table_name
                    and table.get("db_schema") == db_schema
                ):
                    # Format table schema
                    table_key = f"{db_schema}.{table_name}" if db_schema else table_name

                    # Extract column information
                    columns = []
                    for column in table.get("columns", []):
                        column_info = {
                            "name": column["name"],
                            "type": column.get("type", "UNKNOWN"),
                            "description": column.get("description", ""),
                            "is_primary_key": column.get("is_primary_key", False),
                            "is_foreign_key": column.get("is_foreign_key", False),
                            "references": column.get("references", None),
                            "low_cardinality": column.get("low_cardinality", False),
                            "categories": column.get("categories", []),
                        }
                        columns.append(column_info)

                    # Create schema information
                    schema_info = {
                        "table_name": table_name,
                        "db_schema": db_schema,
                        "description": table.get("table_description", ""),
                        "columns": columns,
                        "sql_schema": table.get("table_schema", ""),
                        "examples": table.get("examples", []),
                    }

                    schemas[table_key] = schema_info
                    break

        # Update state
        state.table_schemas = schemas

        # Format schema information for logging
        schema_summary = []
        for table_key, schema in schemas.items():
            column_count = len(schema["columns"])
            schema_summary.append(f"{table_key} ({column_count} columns)")

        logger.info(
            f"Analyzed schemas for {len(schemas)} tables: {', '.join(schema_summary)}"
        )

        return state
    except Exception as e:
        logger.error(f"Error analyzing schemas: {str(e)}")
        # Don't set error state here, as this is not a critical failure
        # We can continue with partial schema information if needed
        return state


# Column Analysis Node


def analyze_columns(state: SQLAgentState) -> SQLAgentState:
    """Analyze relevant columns to gather detailed information.

    This node is responsible for:
    1. Identifying potentially relevant columns from the schema information
    2. Gathering detailed information about those columns
    3. Formatting the column information in a structured way

    Args:
        state: The current state of the SQL agent

    Returns:
        Updated state with relevant column information
    """
    try:
        logger.info("Analyzing columns for relevant tables")

        if not state.table_schemas:
            logger.warning("No table schemas available to analyze columns")
            return state

        # Initialize column information dictionary
        column_info = {}

        # Process each table schema
        for table_key, schema in state.table_schemas.items():
            table_name = schema["table_name"]
            db_schema = schema["db_schema"]

            # Process each column in the table
            for column in schema["columns"]:
                column_name = column["name"]
                column_key = f"{table_key}.{column_name}"

                # Create column information entry
                column_info[column_key] = {
                    "table_name": table_name,
                    "db_schema": db_schema,
                    "column_name": column_name,
                    "type": column["type"],
                    "description": column["description"],
                    "is_primary_key": column["is_primary_key"],
                    "is_foreign_key": column["is_foreign_key"],
                    "references": column["references"],
                    "low_cardinality": column["low_cardinality"],
                    "categories": column["categories"],
                }

                # Add sample values if available
                if "examples" in schema and schema["examples"]:
                    sample_values = []
                    for example in schema["examples"]:
                        if column_name in example and example[column_name] is not None:
                            sample_values.append(str(example[column_name]))

                    if sample_values:
                        column_info[column_key]["sample_values"] = sample_values[
                            :5
                        ]  # Limit to 5 samples

        # Identify potentially relevant columns based on the user's question
        # This is a simple approach - in a more sophisticated implementation,
        # you might use embeddings or other techniques to identify relevant columns
        relevant_columns = {}

        # First, include primary and foreign keys as they're often relevant
        for column_key, info in column_info.items():
            if info["is_primary_key"] or info["is_foreign_key"]:
                relevant_columns[column_key] = info

        # Then, look for columns whose names or descriptions match keywords in the question
        question_lower = state.question.lower()
        for column_key, info in column_info.items():
            # Skip if already included
            if column_key in relevant_columns:
                continue

            # Check if column name appears in the question
            if info["column_name"].lower() in question_lower:
                relevant_columns[column_key] = info
                continue

            # Check if column description contains keywords from the question
            if info["description"]:
                # Simple keyword matching - could be improved with NLP techniques
                description_lower = info["description"].lower()
                # Extract keywords from question (simple approach)
                keywords = [word for word in question_lower.split() if len(word) > 3]
                for keyword in keywords:
                    if keyword in description_lower:
                        relevant_columns[column_key] = info
                        break

        # Update state
        state.relevant_columns = relevant_columns

        # Log results
        logger.info(
            f"Analyzed {len(column_info)} columns, identified {len(relevant_columns)} as potentially relevant"
        )

        return state
    except Exception as e:
        logger.error(f"Error analyzing columns: {str(e)}")
        # Don't set error state here, as this is not a critical failure
        # We can continue with partial column information if needed
        return state


# Query Generation Node


def generate_query(state: SQLAgentState, llm) -> SQLAgentState:
    """Generate SQL query based on collected information.

    This node is responsible for:
    1. Constructing a prompt with all the collected information
    2. Calling the LLM to generate SQL
    3. Extracting the SQL from the LLM response

    Args:
        state: The current state of the SQL agent
        llm: The language model to use for generation

    Returns:
        Updated state with generated SQL query
    """
    try:
        logger.info(f"Generating SQL query for question: {state.question}")

        # Increment iteration count
        state.iteration_count += 1

        # Construct the prompt for the LLM
        prompt = construct_sql_generation_prompt(state)

        # Call the LLM to generate SQL
        logger.info("Calling LLM to generate SQL")
        response = llm.invoke(prompt)

        # Extract SQL from the response
        sql_query = extract_sql_from_response(response)

        if not sql_query:
            logger.warning("No SQL query found in LLM response")
            if state.iteration_count >= state.max_iterations:
                state.error = (
                    "Failed to generate a valid SQL query after maximum iterations"
                )
                state.status = "INVALID"
            return state

        # Update state with generated SQL
        state.generated_sql = sql_query

        logger.info(
            f"Generated SQL query (iteration {state.iteration_count}): {sql_query[:100]}..."
        )

        return state
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        state.error = f"Error generating SQL query: {str(e)}"
        state.status = "INVALID"
        return state


def construct_sql_generation_prompt(state: SQLAgentState) -> str:
    """Construct a prompt for SQL generation based on the state.

    Args:
        state: The current state of the SQL agent

    Returns:
        A prompt string for the LLM
    """
    # Start with the user's question
    prompt = f"### Question\n{state.question}\n\n"

    # Add dialect information if available
    prompt += "### SQL Dialect\n"
    # In a real implementation, you would get the dialect from the database connection
    prompt += "SQL\n\n"  # Default to standard SQL

    # Add relevant tables section
    if state.relevant_tables:
        prompt += "### Relevant Tables\n"
        for table in state.relevant_tables:
            table_name = table.get("table_name", "")
            db_schema = table.get("db_schema", "")
            similarity = table.get("similarity", 0)

            if db_schema:
                prompt += f"- {db_schema}.{table_name} (relevance: {similarity})\n"
            else:
                prompt += f"- {table_name} (relevance: {similarity})\n"
        prompt += "\n"

    # Add table schemas section
    if state.table_schemas:
        prompt += "### Table Schemas\n"
        for table_key, schema in state.table_schemas.items():
            prompt += f"Table: {table_key}\n"
            if schema.get("description"):
                prompt += f"Description: {schema['description']}\n"

            prompt += "Columns:\n"
            for column in schema.get("columns", []):
                column_desc = f"- {column['name']} ({column['type']})"
                if column.get("is_primary_key"):
                    column_desc += " (PRIMARY KEY)"
                if column.get("is_foreign_key"):
                    column_desc += (
                        f" (FOREIGN KEY -> {column.get('references', 'unknown')})"
                    )
                if column.get("description"):
                    column_desc += f": {column['description']}"
                prompt += column_desc + "\n"

            prompt += "\n"

    # Add relevant columns section with sample values
    if state.relevant_columns:
        prompt += "### Relevant Columns with Sample Values\n"
        for column_key, info in state.relevant_columns.items():
            prompt += f"- {column_key}"
            if info.get("description"):
                prompt += f": {info['description']}"
            if info.get("sample_values"):
                prompt += f" (samples: {', '.join(info['sample_values'])})"
            prompt += "\n"
        prompt += "\n"

    # Add few-shot examples if available
    if state.few_shot_examples:
        prompt += "### Similar Examples\n"
        for i, example in enumerate(state.few_shot_examples[:3]):  # Limit to 3 examples
            prompt += f"Example {i+1}:\n"
            prompt += f"Question: {example.get('prompt_text', '')}\n"
            prompt += f"SQL: {example.get('sql', '')}\n\n"

    # Add instructions if available
    if state.instructions:
        prompt += "### Instructions\n"
        for i, instruction in enumerate(state.instructions):
            prompt += f"{i+1}. {instruction.get('instruction', '')}\n"
        prompt += "\n"

    # Add aliases if available
    if state.aliases:
        prompt += "### Aliases\n"
        prompt += "The following aliases are defined and should be replaced with their actual database objects:\n"
        for alias in state.aliases:
            prompt += f"- '{alias.get('name', '')}' refers to {alias.get('target_type', '')} '{alias.get('target_name', '')}'\n"
        prompt += "\n"

    # Add error information if this is a refinement
    if state.iteration_count > 1 and state.error:
        prompt += f"### Previous Error\n{state.error}\n\n"

    # Add final instruction
    prompt += "### Task\n"
    prompt += "Generate a SQL query that answers the question. The query should be syntactically correct and executable.\n"
    prompt += (
        "Return ONLY the SQL query without any explanations or markdown formatting.\n"
    )

    return prompt


def extract_sql_from_response(response: str) -> str:
    """Extract SQL query from LLM response.

    Args:
        response: The response from the LLM

    Returns:
        Extracted SQL query or empty string if not found
    """
    # Try to extract SQL between markdown code blocks
    import re

    # First, try to extract SQL between ```sql and ``` tags
    sql_pattern = r"```sql\s*(.*?)\s*```"
    matches = re.findall(sql_pattern, response, re.DOTALL)
    if matches:
        return matches[0].strip()

    # If that fails, try to extract between just ``` tags
    code_pattern = r"```\s*(.*?)\s*```"
    matches = re.findall(code_pattern, response, re.DOTALL)
    if matches:
        return matches[0].strip()

    # If no code blocks, just return the response as is, assuming it's the SQL
    # Remove any markdown formatting or explanations
    cleaned_response = re.sub(
        r"^.*?SELECT", "SELECT", response, flags=re.DOTALL | re.IGNORECASE
    )

    # If the response starts with SELECT, it's likely a SQL query
    if (
        cleaned_response.strip()
        .upper()
        .startswith(("SELECT", "WITH", "INSERT", "UPDATE", "DELETE"))
    ):
        return cleaned_response.strip()

    # If all else fails, return the original response
    return response.strip()


# Query Validation Node


def validate_query(state: SQLAgentState) -> SQLAgentState:
    """Validate the generated query by executing it against the database.

    This node is responsible for:
    1. Connecting to the database
    2. Executing the generated SQL query
    3. Capturing the result or error

    Args:
        state: The current state of the SQL agent

    Returns:
        Updated state with execution result or error
    """
    try:
        logger.info("Validating generated SQL query")

        if not state.generated_sql:
            logger.warning("No SQL query to validate")
            state.error = "No SQL query was generated"
            state.status = "INVALID"
            return state

        # Get database connection repository
        storage = Storage(Settings())
        db_connection_repository = DatabaseConnectionRepository(storage)

        # Get database connection
        db_connection = db_connection_repository.get_by_id(state.db_connection_id)
        if not db_connection:
            state.error = (
                f"Database connection with ID {state.db_connection_id} not found"
            )
            state.status = "INVALID"
            return state

        # Create SQL database engine
        database = SQLDatabase.get_sql_engine(db_connection)

        # Clean the SQL query
        sql_query = replace_unprocessable_characters(state.generated_sql)

        # Execute the query with timeout
        try:
            from app.utils.core.timeout import run_with_timeout
            import os

            # Get timeout from environment or use default
            timeout_seconds = int(os.getenv("SQL_EXECUTION_TIMEOUT", "60"))

            # Execute query with timeout
            top_k = 10  # Limit to top 10 rows
            result, _ = run_with_timeout(
                database.run_sql,
                args=(sql_query,),
                kwargs={"top_k": top_k},
                timeout_duration=timeout_seconds,
            )

            # Update state with successful execution
            state.execution_result = result
            state.status = "VALID"

            logger.info(f"SQL query executed successfully: {result[:200]}...")

        except TimeoutError:
            state.error = "SQL query execution timed out"
            state.execution_result = "Query execution time exceeded"

            # Don't mark as invalid yet, give a chance to refine
            logger.warning("SQL query execution timed out")

        except Exception as e:
            state.error = f"Error executing SQL query: {str(e)}"
            state.execution_result = f"Error: {str(e)}"

            # Don't mark as invalid yet, give a chance to refine
            logger.warning(f"Error executing SQL query: {str(e)}")

        return state
    except Exception as e:
        logger.error(f"Error validating SQL query: {str(e)}")
        state.error = f"Error validating SQL query: {str(e)}"
        state.status = "INVALID"
        return state


# Response Formatting Node


def format_response(state: SQLAgentState) -> SQLAgentState:
    """Format the final response.

    This node is responsible for:
    1. Setting the completed_at timestamp
    2. Formatting the final SQL query
    3. Adding metadata about the generation process

    Args:
        state: The current state of the SQL agent

    Returns:
        Updated state with formatted response
    """
    try:
        logger.info("Formatting final response")

        # Set completion timestamp
        state.completed_at = str(datetime.now())

        # If we have a valid SQL query, clean it up
        if state.generated_sql:
            state.generated_sql = replace_unprocessable_characters(state.generated_sql)

        # Add metadata about the generation process
        state.metadata["generation_info"] = {
            "iteration_count": state.iteration_count,
            "tables_analyzed": len(state.table_schemas) if state.table_schemas else 0,
            "columns_analyzed": len(state.relevant_columns)
            if state.relevant_columns
            else 0,
            "few_shot_examples_used": len(state.few_shot_examples)
            if state.few_shot_examples
            else 0,
            "instructions_used": len(state.instructions) if state.instructions else 0,
            "aliases_used": len(state.aliases) if state.aliases else 0,
        }

        # Add timing information
        # In a real implementation, you would track the time for each step
        state.metadata["timing"] = {
            "total_time_seconds": (
                datetime.fromisoformat(state.completed_at)
                - datetime.fromisoformat(state.created_at)
            ).total_seconds()
        }

        # Log summary
        if state.status == "VALID":
            logger.info(
                f"Successfully generated SQL query: {state.generated_sql[:100]}..."
            )
        else:
            logger.warning(f"Failed to generate valid SQL query. Error: {state.error}")

        return state
    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}")
        # Don't update status here, as we want to preserve the validation status
        return state


# Conditional Edge Functions


def should_refine_query(state: SQLAgentState) -> str:
    """Determine if the query needs refinement.

    Args:
        state: The current state of the SQL agent

    Returns:
        "refine" if the query needs refinement, "complete" otherwise
    """
    # Check if there's an error in the execution result
    has_error = state.error is not None or (
        state.execution_result and "error" in state.execution_result.lower()
    )

    # If there's an error and we haven't reached the maximum number of iterations,
    # refine the query
    if has_error and state.iteration_count < state.max_iterations:
        logger.info(
            f"Query needs refinement (iteration {state.iteration_count}/{state.max_iterations})"
        )
        return "refine"

    # If we've reached the maximum number of iterations and still have an error,
    # mark as invalid and complete
    if has_error:
        logger.warning(
            f"Maximum iterations reached ({state.max_iterations}) with errors"
        )
        state.status = "INVALID"
        if not state.error:
            state.error = (
                "Failed to generate a valid SQL query after maximum iterations"
            )

    # Otherwise, complete the process
    logger.info("Query validation complete, proceeding to format response")
    return "complete"

from typing import List, Optional
from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import START, END, Graph
from langgraph.graph import MessagesState
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode
import re
import asyncio

from app.data.db.storage import Storage
# from app.server.config import Settings
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.utils.model.chat_model import ChatModel
from app.modules.context_store.models import ContextStore
from app.modules.synthetic_questions.models import (
    QuestionGenerationConfig,
    QuestionSQLPair,
)
from app.utils.question_generator.question_utils import(
    format_table_descriptions_for_prompt,
    build_base_prompt,
    add_user_instruction,
    get_default_instruction_block,
    get_context_store_block,
)

from app.modules.table_description.models import TableDescription
from app.utils.sql_database.sql_database import SQLDatabase

class AgentState(MessagesState):
    """State tracked across agent execution"""

    num_questions_to_generate: int
    sql_dialect: str
    instruction: str | None
    db_intent: str
    table_descriptions: List[TableDescription]
    context_stores: List[ContextStore]
    generated_questions_sql_pairs: List[QuestionSQLPair]
    intents: List[str]
    relevant_tables: List[str]
    relevant_columns: List[str]
    llm: Optional[BaseChatModel]


class QuestionGenerationAgent:
    """
    An agent for generating synthetic questions based on database schema and context stores.

    This agent uses LangGraph to orchestrate a workflow for analyzing context,
    generating questions, validating them, and storing the results.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
    ) -> None:
        self.llm = llm
        # Initialize tools from question_tools.py
        from app.utils.question_generator.question_tools import (
            RelevantTablesInfoTool,
            RelevantColumnsInfoTool,
            SchemaSQLDatabaseTool,
            ExampleQuestionsInfoTool,
        )

        # Create instances of each tool
        # Note: These are placeholder tools and will need to be properly initialized
        # with table_descriptions and context_stores when the agent is run
        tools = [
            RelevantTablesInfoTool(table_descriptions=[]),
            RelevantColumnsInfoTool(table_descriptions=[]),
            SchemaSQLDatabaseTool(table_descriptions=[]),
            ExampleQuestionsInfoTool(),
        ]

        # Initialize the ToolNode with our tools
        self.tools = ToolNode(tools=tools)

    def create_graph(self) -> CompiledGraph:
        """
        Create the question generation workflow graph with LLM agent.

        The graph consists of the following nodes:
        - initial_context_node: Analyze initial provided context (tables and context stores)
        - agent_intents_generator: Generate intents based on the analyzed context
        - generate_questions_sql: Generate synthetic questions based on the intents using LLM with tools
        - tools: Call tools for further context
        - generate_without_tools: Alternative path to generate questions without tools

        Returns:
            CompiledGraph: The configured workflow graph
        """
        # Define the workflow as a graph
        builder = Graph()

        # Add nodes to the graph
        builder.add_node("initial_context_node", self.initial_context_node)
        builder.add_node("agent_intents_generator", self.agent_intents_generator)
        builder.add_node("generate_without_tools", self.generate_without_tools)
        builder.add_node("validate_sql_query", self.validate_sql_query)
        # builder.add_node("generate_questions_sql", self.generate_questions_sql)
        # builder.add_node("tools", self.tools)

        # Add edges to the graph
        builder.add_edge(START, "initial_context_node")
        builder.add_edge("initial_context_node", "agent_intents_generator")

        # Conditional routing based on configuration or other factors
        # For now, we'll use both paths
        builder.add_edge("agent_intents_generator", "generate_without_tools")
        builder.add_edge("generate_without_tools", "validate_sql_query")
        builder.add_edge("validate_sql_query", END)
        # builder.add_edge("agent_intents_generator", "generate_questions_sql")
        # builder.add_conditional_edges("generate_questions_sql", tools_condition)
        # builder.add_edge("tools", "generate_questions_sql")

        # Build and return the graph
        return builder.compile()

    async def initial_context_node(self, state: AgentState) -> AgentState:
        """
        Analyze the provided context (tables and context stores).

        This method examines the table descriptions and context stores to identify
        relevant tables and columns for question generation.
        """
        print("Analyzing context for question generation...")

        # Initialize relevant tables and columns
        state["relevant_tables"] = []
        state["relevant_columns"] = []

        # If we have context stores, analyze them to identify relevant tables
        if state["context_stores"]:
            print(f"Analyzing {len(state['context_stores'])} context stores...")

            # Extract relevant information from context stores
            for context_store in state["context_stores"]:
                # Extract tables and columns from SQL in context store
                # This is a simplified approach - in a real implementation,
                # we would parse the SQL to extract tables and columns
                sql = context_store.sql.lower()

                # Extract table names from SQL (simplified)
                for table in state["table_descriptions"]:
                    table_name = table.table_name.lower()
                    if table_name in sql:
                        state["relevant_tables"].append(table.table_name)

                        # Add columns from this table
                        for column in table.columns:
                            if column.name.lower() in sql:
                                state["relevant_columns"].append(
                                    f"{table.table_name}.{column.name}"
                                )

        # Remove duplicates
        state["relevant_tables"] = list(set(state["relevant_tables"]))
        state["relevant_columns"] = list(set(state["relevant_columns"]))

        if state['relevant_tables']:
            print("="*50)
            print("Relevant Tables and Columns")
            print(state["relevant_columns"])
            print(state["relevant_tables"])
            print("="*50)

        print(
            f"Identified {len(state['relevant_tables'])} relevant tables, "
            f"{len(state['relevant_columns'])} relevant columns"
        )

        return state

    async def agent_intents_generator(self, state: AgentState) -> AgentState:
        """
        Generate intents based on given context using LLM.

        This method uses the LLM to generate n number of intents based on the given context.
        The intents are then stored in the state. to be used by the question generation agent.
        """
    
        table_descriptions = format_table_descriptions_for_prompt(
            state["table_descriptions"], state['relevant_tables'], state['relevant_columns'],
        )
        prompt = build_base_prompt(table_descriptions, state["num_questions_to_generate"])
        prompt = add_user_instruction(prompt, state.get("instruction", ""))
        
        if state.get("context_stores"):
            prompt += get_context_store_block(state["context_stores"])
        else:
            prompt += get_default_instruction_block(state["db_intent"])
        
        # print("="*50)
        # print("Prompt to generate Intents:")
        # if state.get("context_stores"):
        #     print(prompt.replace(table_descriptions, "\n"))
        # else:
        #     print(prompt)
        # print("="*50)
        llm = state["llm"]

        response = await llm.ainvoke(prompt)
        
        intents = response.content
        intents = intents.split("\n")
        intents = [intent.strip() for intent in intents if intent.strip()]
        state["intents"] = intents

        # print("="*50)
        # print("Intents Instructions:")
        # print(get_context_store_block(state["context_stores"]))
        # print("="*50)
        # print("Generated Intents:")
        # print(response.content)
        # print("="*50)

        messages = [
            HumanMessage(
                content=f"Create example questions and SQL queries based on these intents: {intents}"
            )
        ]

        state["messages"] = messages
        return state


    async def validate_sql_query(self, state: AgentState):
        from app.server.config import Settings
        storage = Storage(Settings())
        db_connection_repository = DatabaseConnectionRepository(storage)

        db_connection = db_connection_repository.find_by_id(state['db_connection_id'])
        database = SQLDatabase.get_sql_engine(db_connection, True)

        async def validate_single_query(sql_query):
            try:
                await asyncio.to_thread(database.run_sql, sql_query['sql'], 1)
                sql_query['status'] = 'VALID'
                sql_query['error'] = ''
            except Exception as e:
                sql_query['status'] = 'INVALID'
                sql_query['error'] = str(e)
            return sql_query

        tasks = [validate_single_query(q) for q in state["generated_questions_sql_pairs"]]
        final_sql_query = await asyncio.gather(*tasks)

        state["generated_questions_sql_pairs"] = final_sql_query
        return state

    async def generate_without_tools(self, state: AgentState) -> AgentState:
        """Generate a natural language question and SQL query based on schema and context.
        LLM not capable of using tools. Zero-shot approach.
        """

        table_descriptions = format_table_descriptions_for_prompt(
            state["table_descriptions"], state['relevant_tables'], state['relevant_columns'],
        )
        # Create a system prompt that instructs the LLM on how to generate questions and SQL
        sys_prompt = f"""Generate natural language questions and corresponding SQL queries based on the following context:
        ## Table Descriptions:
        {table_descriptions}
        
        ## Relevant Tables:
        {state["relevant_tables"]}
        
        ## Intents:
        {state["intents"]}
        
        ## Instructions:
        1. For each intent, generate only one clear and specific question that can be answered using SQL.
        2. Then, create a corresponding SQL query that would answer the question.
        3. The SQL query targets the {state['sql_dialect']} SQL dialect.
        
        ## Output Format
        Format your response as list of dictionary objects (JSON) with keys as follows:
        - question: Your natural language question without mentioning the table name.
        - sql: The SQL query that answers the question.

        ## SQL Syntax Rules
        1. If the column name contains space, enclose it in quotes.
        2. If the column name is single word and starts with a capital letter, enclose it in quotes.
        3. Apply CAST(... AS NUMERIC) to the column for all aggregate functions to ensure numeric computation, even if the column is of type TEXT.
        """

        # Create a system message with the prompt
        sys_message = SystemMessage(content=sys_prompt)
        llm = state["llm"]
        # Generate a response using the LLM without tools
        messages = [sys_message] + state["messages"]

        # print("="*50)
        # print("Generating questions SQL prompts without tools:")
        # print(sys_prompt)
        # print("="*50)

        response = await llm.ainvoke(messages)

        # Extract the generated content
        generated_content = response.content

        # Parse the generated content to extract question-SQL pairs
        match = re.search(r"```json(.*?)```", generated_content, re.DOTALL)
        if match:
            pairs = JsonOutputParser().parse(match.group(1))
        else:
            pairs = [
                {
                    "question": '',
                    'sql': '',
                }
            ]

        # Add the generated pairs to the state
        state["generated_questions_sql_pairs"].extend(pairs)

        # For debugging
        print(f"Generated {len(pairs)} question-SQL pairs without tools")

        return state

    async def run(
        self,
        question_generation_config: QuestionGenerationConfig,
        table_descriptions: List[TableDescription],
        context_stores: Optional[List[ContextStore]] = None,
    ) -> List[QuestionSQLPair]:
        """
        Run the question generation workflow with LLM-based navigation.

        This method takes a QuestionGenerationConfig object and related data, creates a state,
        and runs the question generation workflow. The workflow is using an LLM that
        makes decisions based on the context analysis results.

        Args:
            question_generation_config (QuestionGenerationConfig): The question generation configuration
            table_descriptions (List[TableDescription]): List of table descriptions for context
            context_stores (Optional[List[ContextStore]]): Optional list of context stores

        Returns:
            QuestionGenerationConfig: The updated question generation object with generated questions
        """
        # Initialize state with the provided objects
        llm_config = question_generation_config.llm_config
        llm = ChatModel().get_model(
            database_connection=None,
            model_family=llm_config.model_family,
            model_name=llm_config.model_name,
            api_base=llm_config.api_base,
            temperature=0.7,
            max_retries=2,
        )
        state: AgentState = {
            "db_connection_id": question_generation_config.db_connection_id,
            "sql_dialect": question_generation_config.sql_dialect,
            "num_questions_to_generate": question_generation_config.questions_per_batch,
            "db_intent": question_generation_config.db_intent,
            "instruction": question_generation_config.instruction,
            "table_descriptions": table_descriptions,
            "context_stores": context_stores or [],
            "generated_questions_sql_pairs": [],
            "intents": [],
            "relevant_tables": [],
            "relevant_columns": [],
            "llm": llm,
        }

        # Create and run the graph
        print("Starting question generation with LLM Agent")
        graph = self.create_graph()
        final_state = await graph.ainvoke(state)

        # Convert the generated question-SQL pairs to QuestionSQLPair objects
        question_sql_pairs = []
        for row in final_state.get("generated_questions_sql_pairs", []):
            question = row.get("question", "").strip()
            sql = row.get("sql", "").strip()
            status = row.get("status")
            error = row.get("error")
            question_sql_pairs.append(
                QuestionSQLPair(
                    question=question, sql=sql, status=status, error=error
                )
            )

        return question_sql_pairs

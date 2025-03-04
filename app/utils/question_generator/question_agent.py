from typing import List, Optional, TypedDict
from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, END, Graph
from langgraph.graph import MessagesState
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode
from app.utils.model.chat_model import ChatModel
import asyncio

from app.modules.context_store.models import ContextStore
from app.modules.synthetic_questions.models import (
    QuestionGenerationConfig,
    QuestionSQLPair,
)
from app.modules.table_description.models import TableDescription


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
        "description": table_desc.table_description,
        "columns": simplified_columns,
        # Include a small number of examples if available
        "examples": table_desc.examples[:2] if table_desc.examples else [],
    }

    return simplified_table


def format_table_descriptions_for_prompt(
    table_descriptions: List[TableDescription],
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

        formatted_str += f"Table: {simplified['name']}\n"
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


class AgentState(MessagesState):
    """State tracked across agent execution"""

    num_questions_to_generate: int
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
        # builder.add_node("generate_questions_sql", self.generate_questions_sql)
        # builder.add_node("tools", self.tools)

        # Add edges to the graph
        builder.add_edge(START, "initial_context_node")
        builder.add_edge("initial_context_node", "agent_intents_generator")

        # Conditional routing based on configuration or other factors
        # For now, we'll use both paths
        builder.add_edge("agent_intents_generator", "generate_without_tools")
        builder.add_edge("generate_without_tools", END)
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
                            if column.column_name.lower() in sql:
                                state["relevant_columns"].append(
                                    f"{table.table_name}.{column.column_name}"
                                )

        # Remove duplicates
        state["relevant_tables"] = list(set(state["relevant_tables"]))
        state["relevant_columns"] = list(set(state["relevant_columns"]))

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
        prompt = f"""Generate {state["num_questions_to_generate"]} number of relevant intents based on the following context:
        Context: {state["context_stores"]}
        Table Descriptions: {state["table_descriptions"]}
        Format each intents as a single line, with level of details needed

        Example Answer:
        - "I want to know top 5 products with the highest revenue",
        - "I want to know certain employees salaries"
        - "I want to know revenue at certain months"
        - "I want to know number of employees grouped by department"
        """

        llm = state["llm"]

        response = await llm.agenerate([prompt])
        intents = response.generations[0][0].text
        intents = intents.split("\n")
        intents = [intent.strip() for intent in intents if intent.strip()]
        state["intents"] = intents

        messages = [
            HumanMessage(
                content=f"Create example questions and SQL queries based on these intents: {intents}"
            )
        ]

        state["messages"] = messages
        return state

    async def generate_questions_sql(self, state: AgentState) -> AgentState:
        """Generate a natural language question and SQL query based on schema and context.
        LLM capable of using tools to get further context if needed.

        The result will be Question-SQL pair
        """
        # Create a system prompt that instructs the LLM on how to generate questions and SQL
        prompt = f"""Based on the following table descriptions and context, generate natural language questions and corresponding SQL queries:
        Table Descriptions: {state["table_descriptions"]}
        Context Stores: {state["context_stores"]}
        Relevant Tables: {state["relevant_tables"]}
        Intents: {state["intents"]}
        
        For each intent, generate a clear and specific question that can be answered using SQL.
        Then, create a corresponding SQL query that would answer the question.
        
        You can use the available tools to help you understand the database schema and find relevant tables and columns.
        
        Format your response as:
        Question: [Your natural language question]
        SQL: [The SQL query that answers the question]
        """

        # Bind the tools to the LLM
        llm_with_tools = self.llm.bind_tools(
            [tool for tool in self.tools.tools], tool_choice="auto"
        )

        # Create a system message with the prompt
        sys_message = SystemMessage(content=prompt)

        # Generate a response using the LLM with tools
        messages = [sys_message] + state["messages"]
        response = await llm_with_tools.ainvoke([messages])

        # Extract the generated content
        generated_content = response.generations[0][0].text

        # Parse the generated content to extract question-SQL pairs
        # This is a simple implementation - in a real system, you'd want more robust parsing
        pairs = []
        lines = generated_content.split("\n")
        current_question = None
        current_sql = None

        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                # If we already have a question and SQL, add them to pairs
                if current_question and current_sql:
                    pairs.append((current_question, current_sql))

                # Start a new pair
                current_question = line[len("Question:") :].strip()
                current_sql = None
            elif line.startswith("SQL:"):
                current_sql = line[len("SQL:") :].strip()

        # Add the last pair if it exists
        if current_question and current_sql:
            pairs.append((current_question, current_sql))

        # Add the generated pairs to the state
        state["generated_questions_sql_pairs"].extend(pairs)

        # For debugging
        print(f"Generated {len(pairs)} question-SQL pairs")

        return state

    async def generate_without_tools(self, state: AgentState) -> AgentState:
        """Generate a natural language question and SQL query based on schema and context.
        LLM not capable of using tools. Zero-shot approach.
        """
        # Create a system prompt that instructs the LLM on how to generate questions and SQL
        sys_prompt = f"""Generate natural language questions and corresponding SQL queries based on the following context:
        Table Descriptions: {state["table_descriptions"]}
        Context Stores: {state["context_stores"]}
        Relevant Tables: {state["relevant_tables"]}
        Intents: {state["intents"]}
        
        For each intent, generate a clear and specific question that can be answered using SQL.
        Then, create a corresponding SQL query that would answer the question.
        
        Format your response as:
        Question: [Your natural language question]
        SQL: [The SQL query that answers the question]
        """

        # Create a system message with the prompt
        sys_message = SystemMessage(content=sys_prompt)
        llm = state["llm"]
        # Generate a response using the LLM without tools
        messages = [sys_message] + state["messages"]
        response = await llm.agenerate([messages])

        # Extract the generated content
        generated_content = response.generations[0][0].text

        # Parse the generated content to extract question-SQL pairs
        # This is a simple implementation - in a real system, you'd want more robust parsing
        pairs = []
        lines = generated_content.split("\n")
        current_question = None
        current_sql = None

        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                # If we already have a question and SQL, add them to pairs
                if current_question and current_sql:
                    pairs.append((current_question, current_sql))

                # Start a new pair
                current_question = line[len("Question:") :].strip()
                current_sql = None
            elif line.startswith("SQL:"):
                current_sql = line[len("SQL:") :].strip()

        # Add the last pair if it exists
        if current_question and current_sql:
            pairs.append((current_question, current_sql))

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
            "num_questions_to_generate": question_generation_config.questions_per_batch,
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
        for question, sql in final_state.get("generated_questions_sql_pairs", []):
            question_sql_pairs.append(QuestionSQLPair(question=question, sql=sql))

        return question_sql_pairs

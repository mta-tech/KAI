from typing import List, Optional, TypedDict
from uuid import UUID

from langgraph.graph import END, Graph
from langgraph.prebuilt.tool_executor import ToolExecutor
from pydantic import BaseModel

from app.modules.context_store.models import ContextStore
from app.modules.synthetic_questions.models import QuestionGeneration, QuestionSQLPair
from app.modules.table_description.models import TableDescription
from app.utils.question_generator.question_database_toolkit import (
    QuestionDatabaseToolkit,
)


class AgentState(TypedDict):
    """State tracked across agent execution"""

    question_generation: QuestionGeneration
    table_descriptions: List[TableDescription]
    context_stores: List[ContextStore]
    current_batch: int
    current_questions: List[QuestionSQLPair]
    error: Optional[str]


class QuestionGenerationAgent:
    """
    Agent for generating synthetic questions using LangGraph.
    This is a placeholder implementation that will be enhanced with actual LLM integration.
    """

    def __init__(self):
        # Initialize tools
        self.toolkit = QuestionDatabaseToolkit()
        self.tool_executor = ToolExecutor(self.toolkit.get_tools())

    def create_graph(self) -> Graph:
        """
        Create the LangGraph workflow for question generation.
        """
        workflow = Graph()

        # Add nodes
        workflow.add_node("analyze_context", self.analyze_context)
        workflow.add_node("generate_questions", self.generate_questions)
        workflow.add_node("validate_questions", self.validate_questions)
        workflow.add_node("store_results", self.store_results)

        # Add edges
        workflow.add_edge("analyze_context", "generate_questions")
        workflow.add_edge("generate_questions", "validate_questions")
        workflow.add_edge("validate_questions", "store_results")
        workflow.add_edge("store_results", END)

        # Set entry point
        workflow.set_entry_point("analyze_context")

        return workflow

    async def analyze_context(self, state: AgentState) -> AgentState:
        """
        Analyze database context and context stores to prepare for question generation.
        """
        # TODO: Implement context analysis using LLM
        # For now, just pass through the state
        return state

    async def generate_questions(self, state: AgentState) -> AgentState:
        """
        Generate questions based on analyzed context.
        """
        questions_per_batch = state["question_generation"].questions_per_batch
        current_batch = state["current_batch"]

        # TODO: Implement actual question generation using LLM
        # For now, generate placeholder questions
        new_questions = []
        for i in range(questions_per_batch):
            table = state["table_descriptions"][i % len(state["table_descriptions"])]
            question = (
                f"What is the distribution of data in the {table.table_name} table?"
            )
            sql = f"SELECT COUNT(*) FROM {table.table_name} GROUP BY some_column;"
            new_questions.append(QuestionSQLPair(question=question, sql=sql))

        state["current_questions"].extend(new_questions)
        return state

    async def validate_questions(self, state: AgentState) -> AgentState:
        """
        Validate generated questions for quality and correctness.
        """
        if state["question_generation"].evaluate:
            # TODO: Implement question validation using LLM
            pass
        return state

    async def store_results(self, state: AgentState) -> AgentState:
        """
        Store the generated questions in the question generation object.
        """
        state["question_generation"].question_sql_pairs.extend(
            state["current_questions"]
        )
        state["current_batch"] += 1

        # Clear current batch questions
        state["current_questions"] = []

        # Check if we need to continue generating more batches
        if state["current_batch"] < state["question_generation"].num_batches:
            return self.generate_questions(state)

        return state

    async def run(
        self,
        question_generation: QuestionGeneration,
        table_descriptions: List[TableDescription],
        context_stores: List[ContextStore],
    ) -> QuestionGeneration:
        """
        Run the question generation workflow.
        """
        # Initialize state
        state: AgentState = {
            "question_generation": question_generation,
            "table_descriptions": table_descriptions,
            "context_stores": context_stores,
            "current_batch": 0,
            "current_questions": [],
            "error": None,
        }

        # Create and run the graph
        graph = self.create_graph()
        final_state = await graph.arun(state)

        # Return updated question generation object
        return final_state["question_generation"]

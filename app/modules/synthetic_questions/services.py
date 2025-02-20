from typing import List
from app.data.db.storage import Storage

class SyntheticQuestionService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def generate_questions(
        self,
        db_connection_id: str,
        questions_per_batch: int = 5,
        num_batches: int = 1,
        peeking_context_stores: bool = False,
        evaluate: bool = False
    ) -> List[str]:
        """
        Generate synthetic questions based on database schema and optionally context stores.
        
        Args:
            db_connection_id (str): ID of the database connection to use for context
            questions_per_batch (int): Number of questions to generate per batch
            num_batches (int): Number of batches to generate
            peeking_context_stores (bool): Whether to use context stores for additional context
            evaluate (bool): Whether to evaluate generated questions
            
        Returns:
            List[str]: List of generated questions
        """
        # Get database connection details
        db_connection = self.storage.get_database_connection(db_connection_id)
        if not db_connection:
            raise ValueError(f"Database connection {db_connection_id} not found")

        # Get table descriptions for context
        table_descriptions = self.storage.get_table_descriptions(
            db_connection_id=db_connection_id
        )

        # Get context stores if enabled
        context_stores = []
        if peeking_context_stores:
            context_stores = self.storage.get_context_stores(
                db_connection_id=db_connection_id
            )

        # TODO: Implement actual question generation logic using LLM
        # For now, return sample questions
        total_questions = questions_per_batch * num_batches
        sample_questions = [
            f"What is the total number of records in the {desc.table_name} table?"
            for desc in table_descriptions[:total_questions]
        ]

        if len(sample_questions) < total_questions:
            # Add generic questions if we don't have enough table-specific ones
            generic_questions = [
                "What are the relationships between the main tables in the database?",
                "How is the data organized across different schemas?",
                "What are the primary keys used in the major tables?",
                "How are foreign key constraints implemented?",
                "What is the most frequently updated table?"
            ]
            sample_questions.extend(generic_questions[:total_questions - len(sample_questions)])

        return sample_questions[:total_questions]

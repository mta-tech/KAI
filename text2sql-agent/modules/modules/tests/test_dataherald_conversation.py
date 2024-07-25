import unittest
import os
from modules.lib.dataherald_conversation import create_prompt, generate_sql, execute_sql, generate_nl, conversation

class TestConversation(unittest.TestCase):
    db_connection_id = "668269a0c5f260e27b00ff9c"

    def test_conversation_flow(self):
        """Test the entire conversation flow end-to-end"""
        # Step 1: Test creating a prompt in the database
        prompt_id = create_prompt('test prompt', self.db_connection_id)
        self.assertIsNotNone(prompt_id, "Prompt creation failed")
        
        # Step 2: Test generating SQL from a prompt ID
        sql_generation_id, sql_generation, sql_generation_status, sql_generation_score = generate_sql(prompt_id)
        self.assertIsNotNone(sql_generation_id, "SQL generation failed")
        self.assertIsNotNone(sql_generation, "Generated SQL is None")
        
        # Step 3: Test executing SQL generation
        response = execute_sql(sql_generation_id)
        self.assertIsNotNone(response, "SQL execution failed")
        
        # Step 4: Test generating natural language from SQL generation ID
        nl_generation = generate_nl(sql_generation_id)
        self.assertIsNotNone(nl_generation, "Natural language generation failed")
        
        # Step 5: Test end-to-end conversation process
        sql_generation, sql_execution, nl_generation = conversation(self.db_connection_id, 'test prompt')
        self.assertIsNotNone(sql_generation, "Conversation SQL generation failed")
        self.assertIsNotNone(sql_execution, "Conversation SQL execution failed")
        self.assertIsNotNone(nl_generation, "Conversation natural language generation failed")

if __name__ == '__main__':
    unittest.main()
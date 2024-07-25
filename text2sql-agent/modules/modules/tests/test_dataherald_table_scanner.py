import unittest
from unittest.mock import patch, MagicMock
from modules.lib.dataherald_table_scanner import table_scanner

SAMPLE_TABLE_IDS = ["668269a0c5f260e27b00ff9c"]

class TestTableScanner(unittest.TestCase):

    def test_table_scanner_success(self):
        """Test Case 1: Test successful table scanning"""
        # Calling the function
        db_connection_id, table_info = table_scanner(SAMPLE_TABLE_IDS)

        # Assertions
        self.assertIsNotNone(db_connection_id)
        
        self.assertEqual(len(table_info), 1)
        self.assertIsNotNone(table_info[0]['table_id'])
        self.assertIsNotNone(table_info[0]['table_name'])
        self.assertIsNotNone(table_info[0]['table_status'])

    def test_table_scanner_exception(self):
        """Test Case 2: Test exception handling in table scanning"""
        # Calling the function and expecting an exception
        with self.assertRaises(Exception):
            table_scanner(['table1'])

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from modules.lib.dataherald_connector import create_db_uri, connector
from modules.constant.database import DB_TYPE_POSTGRES

class TestDatabaseFunctions(unittest.TestCase):


    def test_create_db_uri_postgres(self):
        """Test Case 1: Test creating a PostgreSQL database URI"""

        uri = create_db_uri(DB_TYPE_POSTGRES, "user", "pass", "localhost", 5432, "dbname")
        expected_uri = "postgresql+psycopg2://user:pass@localhost:5432/dbname"
        self.assertEqual(uri, expected_uri)


    def test_create_db_uri_unsupported_db(self):
        """Test Case 2: Test creating a database URI with an unsupported database type should raise a ValueError"""

        with self.assertRaises(ValueError):
            create_db_uri("unsupported_db", "user", "pass", "localhost", 5432, "dbname")


    @patch('modules.lib.dataherald_connector.DBConnection')
    @patch('modules.lib.dataherald_connector.TableDescription')
    def test_connector(self, mock_table_description, mock_db_connection):
        """Test Case 3: Test the connector function with valid inputs"""
        
        mock_db_connection_instance = MagicMock()
        mock_db_connection_instance.create_database_connection.return_value = {'id': 'test_db_connection_id'}
        mock_db_connection.return_value = mock_db_connection_instance

        mock_table_description_instance = MagicMock()
        mock_table_description_instance.list_table_description.return_value = [
            {'id': 'table1', 'table_name': 'table_name1', 'status': 'SCANNED'},
            {'id': 'table2', 'table_name': 'table_name2', 'status': 'NOT_SCANNED'}
        ]
        mock_table_description.return_value = mock_table_description_instance

        db_connection_id, table_info = connector(DB_TYPE_POSTGRES, "user", "pass", "localhost", 5432, "dbname", ["schema1", "schema2"])

        self.assertEqual(db_connection_id, 'test_db_connection_id')
        self.assertEqual(table_info, [
            {"table_id": 'table1', "table_name": 'table_name1', "table_status": 'SCANNED'},
            {"table_id": 'table2', "table_name": 'table_name2', "table_status": 'NOT_SCANNED'}
        ])


    @patch('modules.lib.dataherald_connector.DBConnection')
    def test_connector_db_connection_error(self, mock_db_connection):
        """Test Case 4: Test the connector function handling a database connection error"""
        
        mock_db_connection_instance = MagicMock()
        mock_db_connection_instance.create_database_connection.side_effect = Exception("DB connection error")
        mock_db_connection.return_value = mock_db_connection_instance

        with self.assertRaises(Exception) as context:
            connector(DB_TYPE_POSTGRES, "user", "pass", "localhost", 5432, "dbname", ["schema1", "schema2"])

        self.assertTrue("Error occurred" in str(context.exception))


    @patch('modules.lib.dataherald_connector.DBConnection')
    @patch('modules.lib.dataherald_connector.TableDescription')
    def test_connector_table_description_error(self, mock_table_description, mock_db_connection):

        """Test Case 5: Test the connector function handling a table description error"""
        mock_db_connection_instance = MagicMock()
        mock_db_connection_instance.create_database_connection.return_value = {'id': 'test_db_connection_id'}
        mock_db_connection.return_value = mock_db_connection_instance

        mock_table_description_instance = MagicMock()
        mock_table_description_instance.list_table_description.side_effect = Exception("Table description error")
        mock_table_description.return_value = mock_table_description_instance

        with self.assertRaises(Exception) as context:
            connector(DB_TYPE_POSTGRES, "user", "pass", "localhost", 5432, "dbname", ["schema1", "schema2"])

        self.assertTrue("Error occurred" in str(context.exception))

if __name__ == '__main__':
    unittest.main()

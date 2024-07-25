import unittest
from unittest.mock import patch, MagicMock
from modules.lib.dataherald_table_status import table_status

SAMPLE_DB_CONNECTION_ID = "667bef4b6265fdf4e328bb3e"

class TestTableStatus(unittest.TestCase):

    def test_table_status_success(self):
        result = table_status(SAMPLE_DB_CONNECTION_ID)
        self.assertIsNotNone(result)


    def test_table_status_failure(self):
        db_connection_id = None
        with self.assertRaises(Exception) as context:
            table_status(db_connection_id)

if __name__ == '__main__':
    unittest.main()

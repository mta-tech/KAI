from sqlalchemy import create_engine, inspect

class DatabaseConnection:

    @staticmethod
    def create_db_connection(db_url):
        engine = create_engine(db_url)
        inspector = inspect(engine)
        db_structure = {}

        tables = inspector.get_table_names()
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            db_structure[table_name] = [column['name'] for column in columns]

        for table, columns in db_structure.items():
            print(f"Table: {table}")
            for column in columns:
                print(f"  Column: {column}")

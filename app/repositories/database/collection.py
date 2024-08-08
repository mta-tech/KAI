from app.repositories.database import DB
import typesense
import logging

logger = logging.getLogger(__name__)

class TypeSenseDB(DB):
    
    def __init__(self, api_key):
        self.client = DB.init_client(api_key)

    def create_collection(self, schema):
        self.client.collections.create(schema)

    def retrieve_collection(self, schema):
        self.client.collections[schema].retrieve()

    def drop_collection(self, schema):
        self.client.collections[schema].delete()

    def update_collection(self, old_schema, updated_schem):
        self.client.collections[old_schema].update(updated_schem)

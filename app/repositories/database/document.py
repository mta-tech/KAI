
from app.repositories.database import DB
import typesense
import logging

logger = logging.getLogger(__name__)

class TypeSenseDB(DB):
    
    def __init__(self, api_key):
        self.client = DB.init_client(api_key)

    def index_document(self, schema, document):
        self.client.collections[schema].documents.create(document)
    
    def retrieve_document(self, schema, document_id):
        self.client.collections[schema].documents[document_id].retrieve()

    def update_document(self, schema, document_id, document):
        self.client.collections[schema].documents[document_id].update(document)

    def update_document_by_query(self, schema, query, document):
        self.client.collections[schema].documents.update(document, query)

    def delete_document(self, schema, document_id):
        self.client.collections[schema].documents[document_id].delete()

    def delete_document_by_query(self, schema, query):
        self.client.collections[schema].documents.delete(query)

    def search_document(self, schema, search_parameter):
        self.client.collections[schema].documents.search(search_parameter)
from app.storage import DB
import typesense
from app.core.config import Settings

class TypeSenseDB:
    @staticmethod
    def create_collection(collection):
        setting = Settings()
        # client = DB.get_client()
        client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": setting.TYPESENSE_HOST,
                        "port": setting.TYPESENSE_PORT,
                        "protocol": setting.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": setting.TYPESENSE_API_KEY,
                # "connection_timeout_seconds": setting.TYPESENSE_TIMEOUT,
            }
        )
        client.collections.create(collection)

    @staticmethod
    def retrieve_collection(collection):
        client = DB.get_client()
        return client.collections[collection].retrieve()

    @staticmethod
    def drop_collection(collection):
        client = DB.get_client()
        client.collections[collection].delete()

    @staticmethod
    def update_collection(old_collection, updated_collection):
        client = DB.get_client()
        client.collections[old_collection].update(updated_collection)

    @staticmethod
    def index_document(collection, document):
        client = DB.get_client()
        client.collections[collection].documents.create(document)

    @staticmethod
    def retrieve_document(collection, document_id):
        client = DB.get_client()
        client.collections[collection].documents[document_id].retrieve()

    @staticmethod
    def update_document(collection, document_id, document):
        client = DB.get_client()
        client.collections[collection].documents[document_id].update(document)

    @staticmethod
    def update_document_by_query(collection, query, document):
        client = DB.get_client()
        client.collections[collection].documents.update(document, query)

    @staticmethod
    def delete_document(collection, document_id):
        client = DB.get_client()
        client.collections[collection].documents[document_id].delete()

    @staticmethod
    def delete_document_by_query(collection, query):
        client = DB.get_client()
        client.collections[collection].documents.delete(query)

    @staticmethod
    def search_document(collection, search_parameter):
        client = DB.get_client()
        client.collections[collection].documents.search(search_parameter)

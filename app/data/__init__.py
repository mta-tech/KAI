from app.data.typesense import TypeSenseDB
from app.server.config import Settings


class Storage(TypeSenseDB):
    def __init__(self, setting: Settings) -> None:
        super().__init__(setting)

    def create_collection(self, collection):
        self.client.collections.create(collection)

    def retrieve_collection(self, collection):
        return self.client.collections[collection].retrieve()

    def drop_collection(self,collection):
        return self.client.collections[collection].delete()

    def update_collection(self,old_collection, updated_collection):
        return self.client.collections[old_collection].update(updated_collection)

    def index_document(self,collection, document):
        return self.client.collections[collection].documents.create(document)

    def retrieve_document(self,collection, document_id):
        return self.client.collections[collection].documents[document_id].retrieve()

    def update_document(self,collection, document_id, document):
        return self.client.collections[collection].documents[document_id].update(document)

    def update_document_by_query(self,collection, query, document):
        return self.client.collections[collection].documents.update(document, query)

    def delete_document(self,collection, document_id):
        return self.client.collections[collection].documents[document_id].delete()

    def delete_document_by_query(self,collection, query):
        return self.client.collections[collection].documents.delete(query)

    def search_document(self,collection, search_parameter):
        return self.client.collections[collection].documents.search(search_parameter)

from app.data.typesense import TypeSenseDB
from app.server.config import Settings


class Storage(TypeSenseDB):
    def __init__(self, setting: Settings) -> None:
        super().__init__(setting)

    def get_collection_schema(self, collection_name):
        return self.get_schema(collection_name)

    def check_collection_exist(self, collection_name):
        existing_collections = self.client.collections.retrieve()
        collection_names = [col["name"] for col in existing_collections]
        return collection_name in collection_names

    def create_collection(self, collection_name):
        if not self.check_collection_exist(collection_name):
            collection_schema = self.get_collection_schema(collection_name)
            result = self.client.collections.create(collection_schema)
            return "created_at" in result

    def retrieve_collection(self, collection_name):
        if self.check_collection_exist(collection_name):
            return self.client.collections[collection_name].retrieve()
        raise LookupError(f"Collection '{collection_name}' not found.")

    def drop_collection(self, collection_name):
        if self.check_collection_exist(collection_name):
            return self.client.collections[collection_name].delete()
        raise LookupError(f"Collection '{collection_name}' not found.")

    def update_collection(self, old_collection, updated_collection):
        if self.check_collection_exist(old_collection):
            return self.client.collections[old_collection].update(updated_collection)
        raise LookupError(f"Collection '{old_collection}' not found.")

    def index_document(self, collection_name, document):
        try:
            if not self.check_collection_exist(collection_name):
                self.create_collection(collection_name)
            created_document = self.client.collections[collection_name].documents.create(document)
            return created_document
        except Exception as e:
            raise e

    def retrieve_document(self, collection_name, document_id):
        if self.check_collection_exist(collection_name):
            try:
                document = (
                    self.client.collections[collection_name]
                    .documents[document_id]
                    .retrieve()
                )
                return created_document
            except Exception as e:
                raise e
        raise LookupError(f"Collection '{collection_name}' not found.")

    def update_document(self, collection_name, document_id, document):
        if self.check_collection_exist(collection_name):
            try:
                updated_document = (
                    self.client.collections[collection_name]
                    .documents[document_id]
                    .update(document)
                )
                return updated_document
            except Exception as e:
                raise e
        raise LookupError(f"Collection '{collection_name}' not found.")

    def update_document_by_query(self, collection_name, query, document):
        if self.check_collection_exist(collection_name):
            try:
                updated_document = self.client.collections[
                    collection_name
                ].documents.update(document, query)
                return updated_document
            except Exception as e:
                raise e
        raise LookupError(f"Collection '{collection_name}' not found.")

    def delete_document(self, collection_name, document_id):
        if self.check_collection_exist(collection_name):
            try:
                result = (
                    self.client.collections[collection_name]
                    .documents[document_id]
                    .delete()
                )
                return "id" in result
            except Exception as e:
                raise e
        raise LookupError(f"Collection '{collection_name}' not found.")

    def delete_document_by_query(self, collection_name, query):
        if self.check_collection_exist(collection_name):
            result = self.client.collections[collection_name].documents.delete(query)
            return result["num_deleted"]

        raise LookupError(f"Collection '{collection_name}' not found.")

    def search_document(self, collection_name, search_parameter):
        if self.check_collection_exist(collection_name):
            found_documents = self.client.collections[collection_name].documents.search(
                search_parameter
            )
            return found_documents
        raise LookupError(f"Collection '{collection_name}' not found.")

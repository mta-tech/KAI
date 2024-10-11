from app.modules.rag.models import DocumentStore

DB_COLLECTION = "documents"

class DocumentRepository:
    def __init__(self, storage):
        self.storage = storage
    
    def insert(self, document: DocumentStore) -> DocumentStore:
        document_dict = document.model_dump(exclude={"id"})
        document.id = str(self.storage.insert_one(DB_COLLECTION, document_dict))
        return document

    def find_by(self, filter: dict, page: int = 0, limit: int = 0) -> list[DocumentStore]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(DocumentStore(**row))
        return result

    def find_by_id(self, id: str) -> DocumentStore | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return DocumentStore(**row)

    def find_all(self) -> list[DocumentStore]:
        rows = self.storage.find_all(DB_COLLECTION, exclude_fields=["text_content"])
        result = [DocumentStore(**row) for row in rows]
        return result
    
    def delete_by_id(self, id: str) -> bool:
        deleted_count = self.storage.delete_by_id(DB_COLLECTION, id)
        return deleted_count > 0 

    def update(self, document: DocumentStore) -> DocumentStore:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": document.id},
            document.model_dump(exclude={"id"}),
        )
        return document
    
# TODO KNOWLEDGE REPOSITORY
class KnowledgeRepository:
    def __init__(self, storage):
        self.storage = storage
    
    def insert(self, document: DocumentStore) -> DocumentStore:
        document_dict = document.model_dump(exclude={"id"})
        document.id = str(self.storage.insert_one(DB_COLLECTION, document_dict))
        return document

    def find_by(self, filter: dict, page: int = 0, limit: int = 0) -> list[DocumentStore]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(DocumentStore(**row))
        return result

    def find_by_id(self, id: str) -> DocumentStore | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return DocumentStore(**row)

    def find_all(self) -> list[DocumentStore]:
        rows = self.storage.find_all(DB_COLLECTION, exclude_fields=["text_content"])
        result = [DocumentStore(**row) for row in rows]
        return result
    
    def delete_by_id(self, id: str) -> bool:
        deleted_count = self.storage.delete_by_id(DB_COLLECTION, id)
        return deleted_count > 0 

    def update(self, document: DocumentStore) -> DocumentStore:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": document.id},
            document.model_dump(exclude={"id"}),
        )
        return document
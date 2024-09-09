from fastapi import HTTPException
from app.api.requests import BusinessGlossaryRequest, UpdateBusinessGlossaryRequest
from app.modules.business_glossary.models import BusinessGlossary
from app.modules.business_glossary.repositories import BusinessGlossaryRepository
from app.modules.database_connection.repositories import DatabaseConnectionRepository


class BusinessGlossaryService:
    def __init__(self, storage):
        self.storage = storage
        self.repository = BusinessGlossaryRepository(self.storage)

    def get_business_glossaries(self, db_connection_id) -> list[BusinessGlossary]:
        filter = {"db_connection_id": db_connection_id}
        return self.repository.find_by(filter)

    def create_business_glossary(
        self, db_connection_id: str, business_glossary_request: BusinessGlossaryRequest
    ) -> BusinessGlossary:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(db_connection_id)
        if not db_connection:
            raise HTTPException(f"Database connection {db_connection_id} not found")

        business_glossary = BusinessGlossary(
            db_connection_id=db_connection_id,
            metric=business_glossary_request.metric,
            alias=business_glossary_request.alias,
            sql=business_glossary_request.sql,
            metadata=business_glossary_request.metadata,
        )
        return self.repository.insert(business_glossary)

    def get_business_glossary(self, business_glossary_id) -> BusinessGlossary:
        business_glossary = self.repository.find_by_id(business_glossary_id)
        if not business_glossary:
            raise HTTPException(f"Business Glossary {business_glossary_id} not found")
        return business_glossary

    def update_business_glossary(
        self, business_glossary_id, request: UpdateBusinessGlossaryRequest
    ) -> BusinessGlossary:
        business_glossary = self.repository.find_by_id(business_glossary_id)
        if not business_glossary:
            raise HTTPException(f"Business Glossary {business_glossary_id} not found")

        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(business_glossary, key, value)

        self.repository.update(business_glossary_id, business_glossary)
        return business_glossary

    def delete_business_glossary(self, business_glossary_id) -> dict:
        business_glossary = self.repository.find_by_id(business_glossary_id)
        if not business_glossary:
            raise HTTPException(f"Business Glossary {business_glossary_id} not found")
        deleted = self.repository.delete(business_glossary_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Business Glossary not deleted")
        return {"status": "success"}

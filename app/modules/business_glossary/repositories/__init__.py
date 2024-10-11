from app.data.db.storage import Storage
from app.modules.business_glossary.models import BusinessGlossary

DB_COLLECTION = "business_glossaries"


class BusinessGlossaryRepository:
    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, business_glossary: BusinessGlossary) -> BusinessGlossary:
        business_glossary_dict = business_glossary.model_dump(exclude={"id"})
        business_glossary.id = str(
            self.storage.insert_one(DB_COLLECTION, business_glossary_dict)
        )
        return business_glossary

    def find_one(self, filter: dict) -> BusinessGlossary | None:
        row = self.storage.find_one(DB_COLLECTION, filter)
        if not row:
            return None
        return BusinessGlossary(**row)

    def find_by_id(self, id: str) -> BusinessGlossary | None:
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return BusinessGlossary(**row)

    def find_by(
        self, filter: dict, page: int = 0, limit: int = 0
    ) -> list[BusinessGlossary]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        result = []
        for row in rows:
            result.append(BusinessGlossary(**row))
        return result

    def find_by_metric(self, prompt: str) -> list[dict]:
        result = []
        rows = self.storage.full_text_search(
            DB_COLLECTION, prompt, columns=["metric", "alias"]
        )
        if rows:
            for row in rows:
                obj = {}
                if row['metric'] in prompt:
                    obj["metric"] = row['metric']
                    obj["sql"] = row['sql']
                else:
                    for alias in row['alias']:
                        if alias in prompt:
                            obj["metric"] = alias
                            obj["sql"] = row['sql']
                            break
                if obj:
                    result.append(obj)
        return result

    def update(
        self,
        business_glossary_id: str,
        business_glossary: BusinessGlossary,
    ) -> BusinessGlossary:
        update_data = business_glossary.model_dump(exclude={"id"})
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": business_glossary_id},
            update_data,
        )
        return business_glossary

    def delete(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)

"""Repository for skill storage in TypeSense."""

from app.data.db.storage import Storage
from app.modules.skill.models import Skill

DB_COLLECTION = "skills"


class SkillRepository:
    """Repository for managing skills in TypeSense storage."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def insert(self, skill: Skill) -> Skill:
        """Insert a new skill."""
        skill_dict = skill.model_dump(exclude={"id"})
        skill.id = str(self.storage.insert_one(DB_COLLECTION, skill_dict))
        return skill

    def find_by_id(self, id: str) -> Skill | None:
        """Find a skill by its TypeSense ID."""
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return Skill(**row)

    def find_by_skill_id(
        self, db_connection_id: str, skill_id: str
    ) -> Skill | None:
        """Find a skill by its skill_id within a database connection."""
        row = self.storage.find_one(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id, "skill_id": skill_id},
        )
        if not row:
            return None
        return Skill(**row)

    def find_by(
        self, filter: dict, page: int = 0, limit: int = 0
    ) -> list[Skill]:
        """Find skills matching a filter."""
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, filter, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, filter)
        return [Skill(**row) for row in rows]

    def find_all_for_connection(self, db_connection_id: str) -> list[Skill]:
        """Find all skills for a database connection."""
        return self.find_by({"db_connection_id": db_connection_id})

    def find_active_for_connection(self, db_connection_id: str) -> list[Skill]:
        """Find all active skills for a database connection."""
        return self.find_by({
            "db_connection_id": db_connection_id,
            "is_active": "true",
        })

    def find_by_relevance(
        self,
        db_connection_id: str,
        query: str,
        query_embedding: list[float],
        limit: int = 5,
        alpha: float = 0.6,
    ) -> list[Skill]:
        """Find skills by semantic relevance to a query.

        Uses hybrid search combining text and vector similarity.
        """
        rows = self.storage.hybrid_search(
            collection=DB_COLLECTION,
            query=query,
            query_by="name, description, content",
            vector_query=f"skill_embedding:({query_embedding}, alpha:{alpha})",
            exclude_fields="skill_embedding",
            filter_by=f"db_connection_id:={db_connection_id}&&is_active:=true",
            limit=limit,
        )
        result = []
        if rows:
            for row in rows:
                if row.get("score", 0) >= 0.3:  # Threshold for relevance
                    result.append(Skill(**row))
        return result

    def search_by_text(
        self,
        db_connection_id: str,
        query: str,
        limit: int = 10,
    ) -> list[Skill]:
        """Search skills by text in name, description, or content."""
        rows = self.storage.full_text_search(
            DB_COLLECTION,
            query,
            columns=["name", "description", "skill_id", "tags"],
        )
        result = []
        if rows:
            for row in rows:
                if row.get("db_connection_id") == db_connection_id:
                    result.append(Skill(**row))
                    if len(result) >= limit:
                        break
        return result

    def update(self, skill: Skill) -> Skill:
        """Update an existing skill."""
        from datetime import datetime

        skill.updated_at = datetime.now().isoformat()
        update_data = skill.model_dump(exclude={"id"})
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": skill.id},
            update_data,
        )
        return skill

    def upsert_by_skill_id(
        self, db_connection_id: str, skill_id: str, skill: Skill
    ) -> Skill:
        """Insert or update a skill by its skill_id."""
        from datetime import datetime

        existing = self.find_by_skill_id(db_connection_id, skill_id)
        if existing:
            skill.id = existing.id
            skill.created_at = existing.created_at
            skill.updated_at = datetime.now().isoformat()
            return self.update(skill)
        else:
            return self.insert(skill)

    def delete(self, id: str) -> int:
        """Delete a skill by ID."""
        return self.storage.delete_by_id(DB_COLLECTION, id)

    def delete_by_skill_id(self, db_connection_id: str, skill_id: str) -> bool:
        """Delete a skill by its skill_id."""
        skill = self.find_by_skill_id(db_connection_id, skill_id)
        if skill and skill.id:
            return self.delete(skill.id) > 0
        return False

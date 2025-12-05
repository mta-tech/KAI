"""Service for skill management and discovery."""

import logging
from pathlib import Path

from fastapi import HTTPException

from app.data.db.storage import Storage
from app.modules.skill.models import Skill, SkillMetadata, SkillDiscoveryResult
from app.modules.skill.repositories import SkillRepository
from app.modules.skill.loader import (
    load_skill_from_file,
    load_skill_metadata,
    derive_skill_id,
)
from app.modules.database_connection.repositories import DatabaseConnectionRepository
from app.utils.model.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


class SkillService:
    """Service for managing skills - discovery, loading, and retrieval."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.repository = SkillRepository(storage)

    def discover_skills(
        self,
        db_connection_id: str,
        skills_path: Path | str,
        sync_to_storage: bool = True,
    ) -> SkillDiscoveryResult:
        """Discover all skills in a directory and optionally sync to storage.

        Scans for SKILL.md files (case-insensitive) recursively and parses
        their frontmatter. Invalid skills are recorded as errors.

        Args:
            db_connection_id: Database connection to associate skills with.
            skills_path: Path to the skills directory to scan.
            sync_to_storage: If True, upsert discovered skills to TypeSense.

        Returns:
            SkillDiscoveryResult with discovered skills and any errors.
        """
        skills_path = Path(skills_path)

        if not skills_path.exists():
            return SkillDiscoveryResult(
                skills=[],
                errors=[f"Skills directory not found: {skills_path}"],
                total_found=0,
                total_errors=1,
            )

        skills: list[SkillMetadata] = []
        errors: list[str] = []

        # Find all SKILL.md files (case-insensitive)
        skill_files = list(skills_path.rglob("[Ss][Kk][Ii][Ll][Ll].[Mm][Dd]"))

        for skill_file in skill_files:
            skill_id = derive_skill_id(skill_file, skills_path)
            try:
                if sync_to_storage:
                    # Load full skill and sync to storage
                    skill = load_skill_from_file(
                        skill_file, skill_id, db_connection_id
                    )
                    # Generate embedding for semantic search
                    skill = self._add_embedding(skill)
                    # Upsert to storage
                    self.repository.upsert_by_skill_id(
                        db_connection_id, skill_id, skill
                    )
                    # Add metadata to result
                    skills.append(SkillMetadata(
                        skill_id=skill.skill_id,
                        name=skill.name,
                        description=skill.description,
                        category=skill.category,
                        tags=skill.tags,
                        is_active=skill.is_active,
                    ))
                else:
                    # Just load metadata for discovery
                    metadata = load_skill_metadata(skill_file, skill_id)
                    skills.append(metadata)

            except Exception as e:
                error_msg = f"Failed to load skill '{skill_id}': {e}"
                errors.append(error_msg)
                logger.warning(error_msg)

        return SkillDiscoveryResult(
            skills=skills,
            errors=errors,
            total_found=len(skills),
            total_errors=len(errors),
        )

    def _add_embedding(self, skill: Skill) -> Skill:
        """Add embedding to skill for semantic search."""
        try:
            embedding_model = EmbeddingModel().get_model()
            # Combine name and description for embedding
            text = f"{skill.name}: {skill.description}"
            skill.skill_embedding = embedding_model.embed_query(text)
        except Exception as e:
            logger.warning(f"Failed to generate embedding for skill '{skill.skill_id}': {e}")
        return skill

    def get_skills(self, db_connection_id: str) -> list[Skill]:
        """Get all skills for a database connection."""
        return self.repository.find_all_for_connection(db_connection_id)

    def get_active_skills(self, db_connection_id: str) -> list[Skill]:
        """Get all active skills for a database connection."""
        return self.repository.find_active_for_connection(db_connection_id)

    def get_skill(self, skill_id: str) -> Skill:
        """Get a skill by its TypeSense ID."""
        skill = self.repository.find_by_id(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")
        return skill

    def get_skill_by_skill_id(
        self, db_connection_id: str, skill_id: str
    ) -> Skill:
        """Get a skill by its skill_id within a database connection."""
        skill = self.repository.find_by_skill_id(db_connection_id, skill_id)
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill '{skill_id}' not found for connection {db_connection_id}",
            )
        return skill

    def find_relevant_skills(
        self,
        db_connection_id: str,
        query: str,
        limit: int = 5,
    ) -> list[Skill]:
        """Find skills relevant to a query using semantic search.

        Args:
            db_connection_id: Database connection to search within.
            query: User's question or query text.
            limit: Maximum number of skills to return.

        Returns:
            List of relevant skills sorted by relevance score.
        """
        try:
            embedding_model = EmbeddingModel().get_model()
            query_embedding = embedding_model.embed_query(query)
            return self.repository.find_by_relevance(
                db_connection_id, query, query_embedding, limit=limit
            )
        except Exception as e:
            logger.warning(f"Semantic search failed, falling back to text search: {e}")
            return self.repository.search_by_text(
                db_connection_id, query, limit=limit
            )

    def search_skills(
        self,
        db_connection_id: str,
        query: str,
        limit: int = 10,
    ) -> list[Skill]:
        """Search skills by text in name, description, or tags."""
        return self.repository.search_by_text(db_connection_id, query, limit=limit)

    def create_skill(
        self,
        db_connection_id: str,
        skill_id: str,
        name: str,
        description: str,
        content: str,
        category: str | None = None,
        tags: list[str] | None = None,
        file_path: str = "",
        metadata: dict | None = None,
    ) -> Skill:
        """Create a new skill programmatically."""
        # Validate database connection exists
        db_repo = DatabaseConnectionRepository(self.storage)
        db_connection = db_repo.find_by_id(db_connection_id)
        if not db_connection:
            raise HTTPException(
                status_code=404,
                detail=f"Database connection {db_connection_id} not found",
            )

        # Check if skill already exists
        existing = self.repository.find_by_skill_id(db_connection_id, skill_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Skill '{skill_id}' already exists",
            )

        skill = Skill(
            db_connection_id=db_connection_id,
            skill_id=skill_id,
            name=name,
            description=description,
            content=content,
            category=category,
            tags=tags or [],
            file_path=file_path,
            metadata=metadata,
        )

        # Add embedding
        skill = self._add_embedding(skill)

        return self.repository.insert(skill)

    def update_skill(
        self,
        db_connection_id: str,
        skill_id: str,
        name: str | None = None,
        description: str | None = None,
        content: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        is_active: bool | None = None,
        metadata: dict | None = None,
    ) -> Skill:
        """Update an existing skill."""
        skill = self.repository.find_by_skill_id(db_connection_id, skill_id)
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill '{skill_id}' not found",
            )

        # Update fields if provided
        if name is not None:
            skill.name = name
        if description is not None:
            skill.description = description
        if content is not None:
            skill.content = content
        if category is not None:
            skill.category = category
        if tags is not None:
            skill.tags = tags
        if is_active is not None:
            skill.is_active = is_active
        if metadata is not None:
            skill.metadata = metadata

        # Re-generate embedding if name or description changed
        if name is not None or description is not None:
            skill = self._add_embedding(skill)

        return self.repository.update(skill)

    def delete_skill(self, db_connection_id: str, skill_id: str) -> bool:
        """Delete a skill by its skill_id."""
        skill = self.repository.find_by_skill_id(db_connection_id, skill_id)
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill '{skill_id}' not found",
            )
        return self.repository.delete_by_skill_id(db_connection_id, skill_id)

    def reload_skill_from_file(
        self,
        db_connection_id: str,
        skill_id: str,
        skills_path: Path | str,
    ) -> Skill:
        """Reload a specific skill from its file.

        Useful when the SKILL.md file has been modified and needs to be re-synced.
        """
        skills_path = Path(skills_path)
        skill_file = skills_path / skill_id / "SKILL.md"

        # Try case-insensitive search
        if not skill_file.exists():
            skill_dir = skills_path / skill_id
            if skill_dir.exists():
                for f in skill_dir.iterdir():
                    if f.name.lower() == "skill.md":
                        skill_file = f
                        break

        if not skill_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Skill file not found: {skill_file}",
            )

        skill = load_skill_from_file(skill_file, skill_id, db_connection_id)
        skill = self._add_embedding(skill)
        return self.repository.upsert_by_skill_id(db_connection_id, skill_id, skill)

    def format_skills_for_prompt(self, db_connection_id: str) -> str:
        """Format all active skills as a list for the agent system prompt."""
        skills = self.get_active_skills(db_connection_id)

        if not skills:
            return "No skills available."

        lines = ["# Available Skills\n"]
        lines.append("Use the `load_skill` tool to load a skill's full instructions.\n")

        for skill in sorted(skills, key=lambda s: s.skill_id):
            lines.append(f"## {skill.skill_id}")
            lines.append(f"**Name:** {skill.name}")
            lines.append(f"**Description:** {skill.description}")
            if skill.category:
                lines.append(f"**Category:** {skill.category}")
            if skill.tags:
                lines.append(f"**Tags:** {', '.join(skill.tags)}")
            lines.append("")

        return "\n".join(lines)

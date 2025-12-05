"""Data models for the skills system."""

from datetime import datetime

from pydantic import BaseModel, Field


class Skill(BaseModel):
    """Full skill definition stored in TypeSense.

    Skills are loaded from SKILL.md files and stored for quick retrieval.
    Supports semantic search via embeddings for finding relevant skills.
    """

    id: str | None = None
    db_connection_id: str = Field(..., description="Database connection this skill belongs to")
    skill_id: str = Field(..., description="Unique skill identifier from directory path (e.g., 'analysis/revenue')")
    name: str = Field(..., description="Human-readable skill name")
    description: str = Field(..., description="When and how to use this skill")
    content: str = Field(..., description="Full markdown content of the skill")
    category: str | None = Field(default=None, description="Optional organizational category")
    tags: list[str] = Field(default_factory=list, description="Optional tags for filtering")
    file_path: str = Field(..., description="Absolute path to the SKILL.md file")
    skill_embedding: list[float] | None = Field(
        default=None, description="Embedding for semantic search"
    )
    is_active: bool = Field(default=True, description="Whether this skill is active")
    metadata: dict | None = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class SkillMetadata(BaseModel):
    """Lightweight skill metadata for discovery and listing.

    Used to show available skills without loading full content.
    """

    skill_id: str
    name: str
    description: str
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True


class SkillDiscoveryResult(BaseModel):
    """Result of scanning for skills in a directory."""

    skills: list[SkillMetadata] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    total_found: int = 0
    total_errors: int = 0

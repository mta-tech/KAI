"""Skills module for KAI.

Provides a skills system that enables AI agents to discover, load, and execute
skill definitions from markdown files with YAML frontmatter.

Skills are stored in TypeSense for quick retrieval and semantic search.
"""

from app.modules.skill.models import Skill, SkillMetadata, SkillDiscoveryResult
from app.modules.skill.repositories import SkillRepository
from app.modules.skill.services import SkillService
from app.modules.skill.loader import (
    parse_frontmatter,
    derive_skill_id,
    load_skill_from_file,
    load_skill_metadata,
)

__all__ = [
    # Models
    "Skill",
    "SkillMetadata",
    "SkillDiscoveryResult",
    # Repository
    "SkillRepository",
    # Service
    "SkillService",
    # Loader
    "parse_frontmatter",
    "derive_skill_id",
    "load_skill_from_file",
    "load_skill_metadata",
]

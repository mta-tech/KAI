"""Skill loading and frontmatter parsing."""

import re
from pathlib import Path
from typing import Any

import yaml

from app.modules.skill.models import Skill, SkillMetadata


# Regex pattern for YAML frontmatter between --- delimiters
FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n?(.*)$",
    re.DOTALL
)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Full markdown content potentially containing frontmatter.

    Returns:
        Tuple of (frontmatter_dict, body_content).
        Returns ({}, content) if no frontmatter found.
    """
    if not content:
        return {}, ""

    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_content, body = match.groups()
    try:
        frontmatter = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        return {}, content

    return frontmatter, body


def derive_skill_id(skill_path: Path, base_path: Path) -> str:
    """Derive skill ID from file path relative to base skills directory.

    Args:
        skill_path: Absolute path to SKILL.md file.
        base_path: Base skills directory path.

    Returns:
        Skill ID derived from directory structure (e.g., "analysis/revenue").
    """
    # Get parent directory of SKILL.md
    skill_dir = skill_path.parent
    # Get relative path from base
    try:
        relative = skill_dir.relative_to(base_path)
        # Convert to forward-slash separated ID
        return str(relative).replace("\\", "/")
    except ValueError:
        # If not relative, use directory name
        return skill_dir.name


def load_skill_from_file(
    skill_path: Path,
    skill_id: str,
    db_connection_id: str,
) -> Skill:
    """Load a skill from a SKILL.md file.

    Args:
        skill_path: Path to the SKILL.md file.
        skill_id: Unique identifier for the skill.
        db_connection_id: Database connection this skill belongs to.

    Returns:
        Skill object with parsed metadata and content.

    Raises:
        FileNotFoundError: If the skill file doesn't exist.
        ValueError: If required frontmatter fields are missing.
    """
    skill_path = Path(skill_path)
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    # Validate required fields
    required_fields = ["name", "description"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        raise ValueError(
            f"Skill '{skill_id}' missing required field(s): {', '.join(missing)}"
        )

    return Skill(
        db_connection_id=db_connection_id,
        skill_id=skill_id,
        name=frontmatter["name"],
        description=frontmatter["description"],
        category=frontmatter.get("category"),
        tags=frontmatter.get("tags", []),
        content=body.strip(),
        file_path=str(skill_path.absolute()),
        is_active=frontmatter.get("is_active", True),
        metadata=frontmatter.get("metadata"),
    )


def load_skill_metadata(
    skill_path: Path,
    skill_id: str,
) -> SkillMetadata:
    """Load only skill metadata from a SKILL.md file.

    Faster than load_skill_from_file when full content isn't needed.

    Args:
        skill_path: Path to the SKILL.md file.
        skill_id: Unique identifier for the skill.

    Returns:
        SkillMetadata object with parsed frontmatter.

    Raises:
        FileNotFoundError: If the skill file doesn't exist.
        ValueError: If required frontmatter fields are missing.
    """
    skill_path = Path(skill_path)
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")
    frontmatter, _ = parse_frontmatter(content)

    # Validate required fields
    required_fields = ["name", "description"]
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        raise ValueError(
            f"Skill '{skill_id}' missing required field(s): {', '.join(missing)}"
        )

    return SkillMetadata(
        skill_id=skill_id,
        name=frontmatter["name"],
        description=frontmatter["description"],
        category=frontmatter.get("category"),
        tags=frontmatter.get("tags", []),
        is_active=frontmatter.get("is_active", True),
    )

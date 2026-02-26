# Python Skills System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a skills system in Python that enables AI agents to discover, load, and execute skill definitions from markdown files with YAML frontmatter.

**Architecture:** Skills are defined as `SKILL.md` files with YAML frontmatter (name, description) stored in a `.skills/` directory hierarchy. A two-tier memory system separates skill metadata (always loaded) from full content (loaded on-demand). The Skill tool loads full instructions into context when invoked.

**Tech Stack:** Python 3.11+, pydantic (data models), pyyaml (frontmatter parsing), pathlib (filesystem), pytest (testing)

---

## Project Structure

```
python-skills/
├── pyproject.toml
├── src/
│   └── skills/
│       ├── __init__.py
│       ├── models.py          # Pydantic data models
│       ├── discovery.py       # Skill discovery logic
│       ├── loader.py          # Skill loading/parsing
│       ├── context.py         # Memory/context management
│       ├── tool.py            # Skill tool implementation
│       └── cli.py             # CLI integration
├── tests/
│   └── skills/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_discovery.py
│       ├── test_loader.py
│       ├── test_context.py
│       └── test_tool.py
└── .skills/
    └── example/
        └── SKILL.md
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/skills/__init__.py`
- Create: `tests/skills/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "python-skills"
version = "0.1.0"
description = "Skills system for AI agents"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Step 2: Create package init files**

```python
# src/skills/__init__.py
"""Python Skills System - Enable AI agents to discover and load skill definitions."""

from skills.models import Skill, SkillMetadata, SkillDiscoveryResult
from skills.discovery import discover_skills
from skills.loader import load_skill, parse_frontmatter
from skills.context import SkillsContext
from skills.tool import skill_tool

__all__ = [
    "Skill",
    "SkillMetadata",
    "SkillDiscoveryResult",
    "discover_skills",
    "load_skill",
    "parse_frontmatter",
    "SkillsContext",
    "skill_tool",
]
```

```python
# tests/skills/__init__.py
"""Tests for the skills system."""
```

**Step 3: Install dependencies**

Run: `pip install -e ".[dev]"`
Expected: Successfully installed python-skills with dependencies

**Step 4: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "chore: initialize python-skills project structure"
```

---

## Task 2: Data Models

**Files:**
- Create: `src/skills/models.py`
- Create: `tests/skills/test_models.py`

**Step 1: Write failing test for SkillMetadata**

```python
# tests/skills/test_models.py
import pytest
from skills.models import SkillMetadata, Skill, SkillDiscoveryResult


class TestSkillMetadata:
    def test_create_with_required_fields(self):
        """SkillMetadata requires id, name, and description."""
        metadata = SkillMetadata(
            id="test-skill",
            name="Test Skill",
            description="A test skill for validation",
        )
        assert metadata.id == "test-skill"
        assert metadata.name == "Test Skill"
        assert metadata.description == "A test skill for validation"
        assert metadata.category is None
        assert metadata.tags == []

    def test_create_with_optional_fields(self):
        """SkillMetadata accepts optional category and tags."""
        metadata = SkillMetadata(
            id="test-skill",
            name="Test Skill",
            description="A test skill",
            category="testing",
            tags=["test", "example"],
        )
        assert metadata.category == "testing"
        assert metadata.tags == ["test", "example"]

    def test_missing_required_field_raises_error(self):
        """SkillMetadata raises ValidationError for missing required fields."""
        with pytest.raises(Exception):  # pydantic.ValidationError
            SkillMetadata(id="test", name="Test")  # missing description


class TestSkill:
    def test_create_skill_with_content(self):
        """Skill extends SkillMetadata with content and path."""
        skill = Skill(
            id="my-skill",
            name="My Skill",
            description="Does something useful",
            content="# Instructions\n\nDo the thing.",
            path="/path/to/.skills/my-skill/SKILL.md",
        )
        assert skill.content == "# Instructions\n\nDo the thing."
        assert skill.path == "/path/to/.skills/my-skill/SKILL.md"


class TestSkillDiscoveryResult:
    def test_create_discovery_result(self):
        """SkillDiscoveryResult holds skills and errors."""
        metadata = SkillMetadata(
            id="skill-1",
            name="Skill One",
            description="First skill",
        )
        result = SkillDiscoveryResult(
            skills=[metadata],
            errors=["Failed to parse .skills/broken/SKILL.md"],
        )
        assert len(result.skills) == 1
        assert len(result.errors) == 1

    def test_empty_discovery_result(self):
        """SkillDiscoveryResult can be empty."""
        result = SkillDiscoveryResult(skills=[], errors=[])
        assert result.skills == []
        assert result.errors == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_models.py -v`
Expected: FAIL with ModuleNotFoundError: No module named 'skills.models'

**Step 3: Write minimal implementation**

```python
# src/skills/models.py
"""Data models for the skills system."""

from pathlib import Path
from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Metadata extracted from SKILL.md frontmatter.

    Used for skill discovery - contains only the information needed
    to identify and describe a skill without loading full content.
    """
    id: str = Field(..., description="Unique skill identifier derived from directory path")
    name: str = Field(..., description="Human-readable skill name")
    description: str = Field(..., description="When and how to use this skill")
    category: str | None = Field(default=None, description="Optional organizational category")
    tags: list[str] = Field(default_factory=list, description="Optional tags for filtering")


class Skill(SkillMetadata):
    """Full skill definition including content.

    Extends SkillMetadata with the actual skill instructions
    loaded from the SKILL.md file body.
    """
    content: str = Field(..., description="Full markdown content of the skill")
    path: str = Field(..., description="Absolute path to the SKILL.md file")


class SkillDiscoveryResult(BaseModel):
    """Result of scanning for skills in a directory.

    Contains successfully parsed skills and any errors encountered
    during discovery (e.g., malformed frontmatter).
    """
    skills: list[SkillMetadata] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_models.py -v`
Expected: PASS (all 5 tests)

**Step 5: Commit**

```bash
git add src/skills/models.py tests/skills/test_models.py
git commit -m "feat: add pydantic data models for skills system"
```

---

## Task 3: Skill Loader (Frontmatter Parsing)

**Files:**
- Create: `src/skills/loader.py`
- Create: `tests/skills/test_loader.py`
- Create: `.skills/example/SKILL.md` (test fixture)

**Step 1: Create test fixture**

```markdown
# .skills/example/SKILL.md
---
name: Example Skill
description: An example skill for testing the loader
category: testing
tags:
  - example
  - test
---

# Example Skill Instructions

This is the body of the skill with detailed instructions.

## Usage

Use this skill when you need an example.
```

**Step 2: Write failing tests for loader**

```python
# tests/skills/test_loader.py
import pytest
from pathlib import Path
from skills.loader import parse_frontmatter, load_skill
from skills.models import Skill


class TestParseFrontmatter:
    def test_parse_valid_frontmatter(self):
        """parse_frontmatter extracts YAML between --- delimiters."""
        content = """---
name: Test Skill
description: A test skill
category: testing
tags:
  - test
---

# Body content here
"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "Test Skill"
        assert frontmatter["description"] == "A test skill"
        assert frontmatter["category"] == "testing"
        assert frontmatter["tags"] == ["test"]
        assert "# Body content here" in body

    def test_parse_frontmatter_minimal(self):
        """parse_frontmatter works with minimal frontmatter."""
        content = """---
name: Minimal
description: Just the basics
---

Body
"""
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "Minimal"
        assert frontmatter["description"] == "Just the basics"
        assert "category" not in frontmatter
        assert body.strip() == "Body"

    def test_parse_frontmatter_no_frontmatter(self):
        """parse_frontmatter returns empty dict for content without frontmatter."""
        content = "# Just markdown\n\nNo frontmatter here."
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}
        assert "# Just markdown" in body

    def test_parse_frontmatter_empty_content(self):
        """parse_frontmatter handles empty content."""
        frontmatter, body = parse_frontmatter("")
        assert frontmatter == {}
        assert body == ""


class TestLoadSkill:
    def test_load_skill_from_file(self, tmp_path: Path):
        """load_skill reads and parses a SKILL.md file."""
        skill_dir = tmp_path / ".skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: Test Skill
description: A skill for testing
tags:
  - test
---

# Instructions

Do the test thing.
""")
        skill = load_skill(skill_file, skill_id="test-skill")

        assert skill.id == "test-skill"
        assert skill.name == "Test Skill"
        assert skill.description == "A skill for testing"
        assert skill.tags == ["test"]
        assert "# Instructions" in skill.content
        assert str(skill_file) in skill.path

    def test_load_skill_missing_name_raises_error(self, tmp_path: Path):
        """load_skill raises ValueError for missing required fields."""
        skill_dir = tmp_path / ".skills" / "bad-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
description: Missing the name field
---

Body
""")
        with pytest.raises(ValueError, match="missing required field.*name"):
            load_skill(skill_file, skill_id="bad-skill")

    def test_load_skill_file_not_found(self, tmp_path: Path):
        """load_skill raises FileNotFoundError for missing file."""
        missing_file = tmp_path / "nonexistent" / "SKILL.md"
        with pytest.raises(FileNotFoundError):
            load_skill(missing_file, skill_id="nonexistent")
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/skills/test_loader.py -v`
Expected: FAIL with ModuleNotFoundError: No module named 'skills.loader'

**Step 4: Write minimal implementation**

```python
# src/skills/loader.py
"""Skill loading and frontmatter parsing."""

import re
from pathlib import Path
from typing import Any

import yaml

from skills.models import Skill


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


def load_skill(skill_path: Path, skill_id: str) -> Skill:
    """Load a skill from a SKILL.md file.

    Args:
        skill_path: Path to the SKILL.md file.
        skill_id: Unique identifier for the skill (typically from directory structure).

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
        id=skill_id,
        name=frontmatter["name"],
        description=frontmatter["description"],
        category=frontmatter.get("category"),
        tags=frontmatter.get("tags", []),
        content=body.strip(),
        path=str(skill_path.absolute()),
    )
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/skills/test_loader.py -v`
Expected: PASS (all 7 tests)

**Step 6: Commit**

```bash
git add src/skills/loader.py tests/skills/test_loader.py .skills/
git commit -m "feat: add skill loader with frontmatter parsing"
```

---

## Task 4: Skill Discovery

**Files:**
- Create: `src/skills/discovery.py`
- Create: `tests/skills/test_discovery.py`

**Step 1: Write failing tests for discovery**

```python
# tests/skills/test_discovery.py
import pytest
from pathlib import Path
from skills.discovery import discover_skills, derive_skill_id


class TestDeriveSkillId:
    def test_simple_skill_id(self):
        """derive_skill_id extracts ID from simple directory."""
        base = Path("/project/.skills")
        skill_path = Path("/project/.skills/my-skill/SKILL.md")
        assert derive_skill_id(skill_path, base) == "my-skill"

    def test_nested_skill_id(self):
        """derive_skill_id handles nested directories."""
        base = Path("/project/.skills")
        skill_path = Path("/project/.skills/web/scraper/SKILL.md")
        assert derive_skill_id(skill_path, base) == "web/scraper"

    def test_deeply_nested_skill_id(self):
        """derive_skill_id handles deeply nested directories."""
        base = Path("/project/.skills")
        skill_path = Path("/project/.skills/tools/code/python/formatter/SKILL.md")
        assert derive_skill_id(skill_path, base) == "tools/code/python/formatter"


class TestDiscoverSkills:
    def test_discover_single_skill(self, tmp_path: Path):
        """discover_skills finds a single skill."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: A test skill
---

Body
""")
        result = discover_skills(skills_dir)

        assert len(result.skills) == 1
        assert result.skills[0].id == "test-skill"
        assert result.skills[0].name == "Test Skill"
        assert len(result.errors) == 0

    def test_discover_multiple_skills(self, tmp_path: Path):
        """discover_skills finds multiple skills."""
        skills_dir = tmp_path / ".skills"

        for name in ["skill-a", "skill-b", "skill-c"]:
            skill_dir = skills_dir / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(f"""---
name: {name.title()}
description: Description for {name}
---

Body for {name}
""")
        result = discover_skills(skills_dir)

        assert len(result.skills) == 3
        skill_ids = {s.id for s in result.skills}
        assert skill_ids == {"skill-a", "skill-b", "skill-c"}

    def test_discover_nested_skills(self, tmp_path: Path):
        """discover_skills finds nested skills with hierarchical IDs."""
        skills_dir = tmp_path / ".skills"

        # Create nested skill
        nested_dir = skills_dir / "web" / "scraper"
        nested_dir.mkdir(parents=True)
        (nested_dir / "SKILL.md").write_text("""---
name: Web Scraper
description: Scrape web pages
---

Body
""")
        result = discover_skills(skills_dir)

        assert len(result.skills) == 1
        assert result.skills[0].id == "web/scraper"

    def test_discover_handles_malformed_skill(self, tmp_path: Path):
        """discover_skills records errors for malformed skills."""
        skills_dir = tmp_path / ".skills"

        # Valid skill
        good_dir = skills_dir / "good-skill"
        good_dir.mkdir(parents=True)
        (good_dir / "SKILL.md").write_text("""---
name: Good Skill
description: Valid skill
---

Body
""")
        # Invalid skill (missing description)
        bad_dir = skills_dir / "bad-skill"
        bad_dir.mkdir(parents=True)
        (bad_dir / "SKILL.md").write_text("""---
name: Bad Skill
---

No description
""")
        result = discover_skills(skills_dir)

        assert len(result.skills) == 1
        assert result.skills[0].id == "good-skill"
        assert len(result.errors) == 1
        assert "bad-skill" in result.errors[0]

    def test_discover_empty_directory(self, tmp_path: Path):
        """discover_skills returns empty result for empty directory."""
        skills_dir = tmp_path / ".skills"
        skills_dir.mkdir()

        result = discover_skills(skills_dir)

        assert len(result.skills) == 0
        assert len(result.errors) == 0

    def test_discover_nonexistent_directory(self, tmp_path: Path):
        """discover_skills returns empty result for nonexistent directory."""
        skills_dir = tmp_path / "nonexistent"

        result = discover_skills(skills_dir)

        assert len(result.skills) == 0
        assert len(result.errors) == 0

    def test_discover_case_insensitive_skill_md(self, tmp_path: Path):
        """discover_skills finds SKILL.md regardless of case."""
        skills_dir = tmp_path / ".skills"

        # Lowercase
        skill_a = skills_dir / "skill-a"
        skill_a.mkdir(parents=True)
        (skill_a / "skill.md").write_text("""---
name: Skill A
description: Lowercase filename
---
Body
""")
        # Mixed case
        skill_b = skills_dir / "skill-b"
        skill_b.mkdir(parents=True)
        (skill_b / "Skill.MD").write_text("""---
name: Skill B
description: Mixed case filename
---
Body
""")
        result = discover_skills(skills_dir)

        assert len(result.skills) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_discovery.py -v`
Expected: FAIL with ModuleNotFoundError: No module named 'skills.discovery'

**Step 3: Write minimal implementation**

```python
# src/skills/discovery.py
"""Skill discovery - recursively scan directories for SKILL.md files."""

from pathlib import Path

from skills.loader import load_skill
from skills.models import SkillDiscoveryResult, SkillMetadata


def derive_skill_id(skill_path: Path, base_path: Path) -> str:
    """Derive skill ID from file path relative to base skills directory.

    Args:
        skill_path: Absolute path to SKILL.md file.
        base_path: Base skills directory path.

    Returns:
        Skill ID derived from directory structure (e.g., "web/scraper").
    """
    # Get parent directory of SKILL.md
    skill_dir = skill_path.parent
    # Get relative path from base
    relative = skill_dir.relative_to(base_path)
    # Convert to forward-slash separated ID
    return str(relative).replace("\\", "/")


def discover_skills(skills_path: Path | str) -> SkillDiscoveryResult:
    """Discover all skills in a directory recursively.

    Scans for SKILL.md files (case-insensitive) and parses their
    frontmatter to extract metadata. Invalid skills are recorded
    as errors but don't stop discovery.

    Args:
        skills_path: Path to the skills directory to scan.

    Returns:
        SkillDiscoveryResult containing discovered skills and any errors.
    """
    skills_path = Path(skills_path)

    if not skills_path.exists():
        return SkillDiscoveryResult(skills=[], errors=[])

    skills: list[SkillMetadata] = []
    errors: list[str] = []

    # Find all SKILL.md files (case-insensitive)
    skill_files = list(skills_path.rglob("[Ss][Kk][Ii][Ll][Ll].[Mm][Dd]"))

    for skill_file in skill_files:
        skill_id = derive_skill_id(skill_file, skills_path)
        try:
            skill = load_skill(skill_file, skill_id)
            # Convert to metadata only (don't store full content in discovery)
            metadata = SkillMetadata(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                category=skill.category,
                tags=skill.tags,
            )
            skills.append(metadata)
        except Exception as e:
            errors.append(f"Failed to load skill '{skill_id}': {e}")

    return SkillDiscoveryResult(skills=skills, errors=errors)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_discovery.py -v`
Expected: PASS (all 9 tests)

**Step 5: Commit**

```bash
git add src/skills/discovery.py tests/skills/test_discovery.py
git commit -m "feat: add recursive skill discovery"
```

---

## Task 5: Skills Context (Memory Management)

**Files:**
- Create: `src/skills/context.py`
- Create: `tests/skills/test_context.py`

**Step 1: Write failing tests for context**

```python
# tests/skills/test_context.py
import pytest
from pathlib import Path
from skills.context import SkillsContext
from skills.models import SkillMetadata


class TestSkillsContext:
    def test_create_empty_context(self):
        """SkillsContext initializes with empty state."""
        ctx = SkillsContext()
        assert ctx.get_all_metadata() == []
        assert ctx.get_loaded_skills() == []
        assert ctx.is_skill_loaded("any-skill") is False

    def test_set_discovered_skills(self):
        """SkillsContext stores discovered skill metadata."""
        ctx = SkillsContext()
        metadata = [
            SkillMetadata(id="skill-a", name="Skill A", description="First skill"),
            SkillMetadata(id="skill-b", name="Skill B", description="Second skill"),
        ]
        ctx.set_discovered_skills(metadata)

        assert len(ctx.get_all_metadata()) == 2
        assert ctx.get_metadata("skill-a") is not None
        assert ctx.get_metadata("skill-a").name == "Skill A"

    def test_load_skill(self, tmp_path: Path):
        """SkillsContext loads full skill content."""
        # Create skill file
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: A test skill
---

# Instructions

Do the thing.
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        metadata = SkillMetadata(
            id="test-skill",
            name="Test Skill",
            description="A test skill",
        )
        ctx.set_discovered_skills([metadata])

        # Load the skill
        skill = ctx.load_skill("test-skill")

        assert skill is not None
        assert skill.id == "test-skill"
        assert "# Instructions" in skill.content
        assert ctx.is_skill_loaded("test-skill") is True

    def test_load_skill_already_loaded(self, tmp_path: Path):
        """SkillsContext returns cached skill if already loaded."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: A test skill
---

Content
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        ctx.set_discovered_skills([
            SkillMetadata(id="test-skill", name="Test", description="Test"),
        ])

        skill1 = ctx.load_skill("test-skill")
        skill2 = ctx.load_skill("test-skill")

        assert skill1 is skill2  # Same object

    def test_load_skill_not_discovered(self):
        """SkillsContext raises error for unknown skill."""
        ctx = SkillsContext()
        with pytest.raises(ValueError, match="not found"):
            ctx.load_skill("unknown-skill")

    def test_unload_skill(self, tmp_path: Path):
        """SkillsContext can unload a skill."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: A test skill
---

Content
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        ctx.set_discovered_skills([
            SkillMetadata(id="test-skill", name="Test", description="Test"),
        ])

        ctx.load_skill("test-skill")
        assert ctx.is_skill_loaded("test-skill") is True

        ctx.unload_skill("test-skill")
        assert ctx.is_skill_loaded("test-skill") is False

    def test_get_loaded_skills_content(self, tmp_path: Path):
        """SkillsContext returns formatted loaded skills content."""
        skills_dir = tmp_path / ".skills"

        for name in ["skill-a", "skill-b"]:
            skill_dir = skills_dir / name
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(f"""---
name: {name.title()}
description: Description for {name}
---

# {name.title()} Instructions

Content for {name}.
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        ctx.set_discovered_skills([
            SkillMetadata(id="skill-a", name="Skill-A", description="Desc A"),
            SkillMetadata(id="skill-b", name="Skill-B", description="Desc B"),
        ])

        ctx.load_skill("skill-a")
        ctx.load_skill("skill-b")

        loaded = ctx.get_loaded_skills()
        assert len(loaded) == 2

        content = ctx.format_loaded_skills()
        assert "# Skill: skill-a" in content
        assert "# Skill: skill-b" in content
        assert "---" in content  # Separator

    def test_format_metadata_for_prompt(self):
        """SkillsContext formats metadata for agent prompt."""
        ctx = SkillsContext()
        ctx.set_discovered_skills([
            SkillMetadata(
                id="web/scraper",
                name="Web Scraper",
                description="Scrape content from websites",
                category="web",
                tags=["scraping", "http"],
            ),
            SkillMetadata(
                id="code/formatter",
                name="Code Formatter",
                description="Format source code",
            ),
        ])

        formatted = ctx.format_metadata_for_prompt()

        assert "web/scraper" in formatted
        assert "Web Scraper" in formatted
        assert "Scrape content" in formatted
        assert "code/formatter" in formatted
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_context.py -v`
Expected: FAIL with ModuleNotFoundError: No module named 'skills.context'

**Step 3: Write minimal implementation**

```python
# src/skills/context.py
"""Skills context - manages skill metadata and loaded skills state."""

from pathlib import Path

from skills.loader import load_skill
from skills.models import Skill, SkillMetadata


class SkillsContext:
    """Manages skill discovery metadata and loaded skill content.

    Implements the two-tier memory system:
    - Metadata tier: Always available, contains skill IDs/names/descriptions
    - Loaded tier: On-demand, contains full skill instructions
    """

    def __init__(self, skills_dir: Path | str | None = None):
        """Initialize skills context.

        Args:
            skills_dir: Path to the .skills directory. Defaults to ./.skills
        """
        self._skills_dir = Path(skills_dir) if skills_dir else Path(".skills")
        self._metadata: dict[str, SkillMetadata] = {}
        self._loaded: dict[str, Skill] = {}

    @property
    def skills_dir(self) -> Path:
        """Get the skills directory path."""
        return self._skills_dir

    def set_discovered_skills(self, skills: list[SkillMetadata]) -> None:
        """Set the discovered skills metadata.

        Args:
            skills: List of skill metadata from discovery.
        """
        self._metadata = {s.id: s for s in skills}

    def get_all_metadata(self) -> list[SkillMetadata]:
        """Get all discovered skill metadata."""
        return list(self._metadata.values())

    def get_metadata(self, skill_id: str) -> SkillMetadata | None:
        """Get metadata for a specific skill."""
        return self._metadata.get(skill_id)

    def is_skill_loaded(self, skill_id: str) -> bool:
        """Check if a skill is currently loaded."""
        return skill_id in self._loaded

    def get_loaded_skills(self) -> list[Skill]:
        """Get all currently loaded skills."""
        return list(self._loaded.values())

    def load_skill(self, skill_id: str) -> Skill:
        """Load a skill by ID.

        Args:
            skill_id: The skill identifier to load.

        Returns:
            The loaded Skill object.

        Raises:
            ValueError: If the skill is not found in discovered skills.
            FileNotFoundError: If the skill file doesn't exist.
        """
        # Return cached if already loaded
        if skill_id in self._loaded:
            return self._loaded[skill_id]

        # Check if skill was discovered
        if skill_id not in self._metadata:
            raise ValueError(f"Skill '{skill_id}' not found in discovered skills")

        # Build path to skill file
        skill_path = self._skills_dir / skill_id / "SKILL.md"

        # Try case-insensitive search if exact path doesn't exist
        if not skill_path.exists():
            skill_dir = self._skills_dir / skill_id
            if skill_dir.exists():
                for f in skill_dir.iterdir():
                    if f.name.lower() == "skill.md":
                        skill_path = f
                        break

        # Load and cache the skill
        skill = load_skill(skill_path, skill_id)
        self._loaded[skill_id] = skill
        return skill

    def unload_skill(self, skill_id: str) -> bool:
        """Unload a skill from the loaded state.

        Args:
            skill_id: The skill identifier to unload.

        Returns:
            True if the skill was unloaded, False if it wasn't loaded.
        """
        if skill_id in self._loaded:
            del self._loaded[skill_id]
            return True
        return False

    def format_loaded_skills(self) -> str:
        """Format loaded skills for inclusion in agent context.

        Returns:
            Formatted string with all loaded skill content.
        """
        if not self._loaded:
            return "[CURRENTLY EMPTY]"

        parts = []
        for skill in self._loaded.values():
            parts.append(f"# Skill: {skill.id}\n\n{skill.content}")

        return "\n\n---\n\n".join(parts)

    def format_metadata_for_prompt(self) -> str:
        """Format skill metadata for agent system prompt.

        Returns:
            Formatted string listing all available skills.
        """
        if not self._metadata:
            return "No skills available."

        lines = ["# Available Skills\n"]
        for skill in sorted(self._metadata.values(), key=lambda s: s.id):
            lines.append(f"## {skill.id}")
            lines.append(f"**Name:** {skill.name}")
            lines.append(f"**Description:** {skill.description}")
            if skill.category:
                lines.append(f"**Category:** {skill.category}")
            if skill.tags:
                lines.append(f"**Tags:** {', '.join(skill.tags)}")
            lines.append("")

        return "\n".join(lines)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_context.py -v`
Expected: PASS (all 9 tests)

**Step 5: Commit**

```bash
git add src/skills/context.py tests/skills/test_context.py
git commit -m "feat: add skills context for memory management"
```

---

## Task 6: Skill Tool

**Files:**
- Create: `src/skills/tool.py`
- Create: `tests/skills/test_tool.py`

**Step 1: Write failing tests for skill tool**

```python
# tests/skills/test_tool.py
import pytest
from pathlib import Path
from skills.tool import skill_tool, SkillToolResult
from skills.context import SkillsContext
from skills.models import SkillMetadata


class TestSkillTool:
    def test_load_skill_success(self, tmp_path: Path):
        """skill_tool loads a skill and returns success."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: A test skill
---

# Instructions

Do the thing.
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        ctx.set_discovered_skills([
            SkillMetadata(id="test-skill", name="Test", description="Test"),
        ])

        result = skill_tool("test-skill", ctx)

        assert result.success is True
        assert result.skill_id == "test-skill"
        assert "# Instructions" in result.content
        assert result.error is None

    def test_load_skill_already_loaded(self, tmp_path: Path):
        """skill_tool returns message if skill already loaded."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: A test skill
---

Content
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        ctx.set_discovered_skills([
            SkillMetadata(id="test-skill", name="Test", description="Test"),
        ])

        # Load once
        skill_tool("test-skill", ctx)

        # Load again
        result = skill_tool("test-skill", ctx)

        assert result.success is True
        assert result.already_loaded is True

    def test_load_skill_not_found(self):
        """skill_tool returns error for unknown skill."""
        ctx = SkillsContext()

        result = skill_tool("unknown-skill", ctx)

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_load_skill_with_nested_id(self, tmp_path: Path):
        """skill_tool handles nested skill IDs."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "web" / "scraper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Web Scraper
description: Scrape websites
---

Scraping instructions.
""")
        ctx = SkillsContext(skills_dir=skills_dir)
        ctx.set_discovered_skills([
            SkillMetadata(id="web/scraper", name="Scraper", description="Scrape"),
        ])

        result = skill_tool("web/scraper", ctx)

        assert result.success is True
        assert result.skill_id == "web/scraper"


class TestSkillToolResult:
    def test_result_to_dict(self):
        """SkillToolResult converts to dictionary."""
        result = SkillToolResult(
            success=True,
            skill_id="test",
            content="Content",
        )
        d = result.to_dict()

        assert d["success"] is True
        assert d["skill_id"] == "test"
        assert d["content"] == "Content"

    def test_result_str_representation(self):
        """SkillToolResult has useful string representation."""
        result = SkillToolResult(
            success=True,
            skill_id="test",
            content="# Instructions\n\nDo stuff.",
        )
        s = str(result)

        assert "test" in s
        assert "Instructions" in s
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_tool.py -v`
Expected: FAIL with ModuleNotFoundError: No module named 'skills.tool'

**Step 3: Write minimal implementation**

```python
# src/skills/tool.py
"""Skill tool - loads skills into agent context on demand."""

from dataclasses import dataclass, field
from typing import Any

from skills.context import SkillsContext


@dataclass
class SkillToolResult:
    """Result of invoking the skill tool."""

    success: bool
    skill_id: str | None = None
    content: str | None = None
    already_loaded: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "skill_id": self.skill_id,
            "content": self.content,
            "already_loaded": self.already_loaded,
            "error": self.error,
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        if not self.success:
            return f"Skill tool error: {self.error}"
        if self.already_loaded:
            return f"Skill '{self.skill_id}' is already loaded."
        return f"Loaded skill '{self.skill_id}':\n\n{self.content}"


def skill_tool(skill_id: str, context: SkillsContext) -> SkillToolResult:
    """Load a skill into the agent context.

    This is the main entry point for the skill tool that agents call
    when they need to load a skill's full instructions.

    Args:
        skill_id: The ID of the skill to load (e.g., "web/scraper").
        context: The SkillsContext managing skill state.

    Returns:
        SkillToolResult indicating success or failure.
    """
    # Check if already loaded
    if context.is_skill_loaded(skill_id):
        skill = context.get_loaded_skills()
        loaded_skill = next((s for s in skill if s.id == skill_id), None)
        return SkillToolResult(
            success=True,
            skill_id=skill_id,
            content=loaded_skill.content if loaded_skill else None,
            already_loaded=True,
        )

    # Try to load the skill
    try:
        skill = context.load_skill(skill_id)
        return SkillToolResult(
            success=True,
            skill_id=skill_id,
            content=skill.content,
            already_loaded=False,
        )
    except ValueError as e:
        return SkillToolResult(
            success=False,
            skill_id=skill_id,
            error=str(e),
        )
    except FileNotFoundError as e:
        return SkillToolResult(
            success=False,
            skill_id=skill_id,
            error=f"Skill file not found: {e}",
        )
    except Exception as e:
        return SkillToolResult(
            success=False,
            skill_id=skill_id,
            error=f"Failed to load skill: {e}",
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_tool.py -v`
Expected: PASS (all 6 tests)

**Step 5: Commit**

```bash
git add src/skills/tool.py tests/skills/test_tool.py
git commit -m "feat: add skill tool for loading skills on demand"
```

---

## Task 7: CLI Integration

**Files:**
- Create: `src/skills/cli.py`
- Create: `tests/skills/test_cli.py`

**Step 1: Write failing tests for CLI**

```python
# tests/skills/test_cli.py
import pytest
from pathlib import Path
from skills.cli import SkillsCLI


class TestSkillsCLI:
    def test_init_with_default_path(self, tmp_path: Path, monkeypatch):
        """SkillsCLI uses .skills in current directory by default."""
        monkeypatch.chdir(tmp_path)
        skills_dir = tmp_path / ".skills"
        skills_dir.mkdir()

        cli = SkillsCLI()

        assert cli.context.skills_dir == Path(".skills")

    def test_init_with_custom_path(self, tmp_path: Path):
        """SkillsCLI accepts custom skills directory."""
        custom_dir = tmp_path / "my-skills"
        custom_dir.mkdir()

        cli = SkillsCLI(skills_dir=custom_dir)

        assert cli.context.skills_dir == custom_dir

    def test_discover_and_list(self, tmp_path: Path):
        """SkillsCLI discovers and lists skills."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: My Skill
description: Does something
---

Body
""")
        cli = SkillsCLI(skills_dir=skills_dir)
        cli.discover()

        skills = cli.list_skills()

        assert len(skills) == 1
        assert skills[0].id == "my-skill"

    def test_load_skill_via_cli(self, tmp_path: Path):
        """SkillsCLI can load a skill."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Test Skill
description: For testing
---

# Instructions

Test instructions here.
""")
        cli = SkillsCLI(skills_dir=skills_dir)
        cli.discover()

        result = cli.load("test-skill")

        assert result.success is True
        assert "# Instructions" in result.content

    def test_get_system_prompt_components(self, tmp_path: Path):
        """SkillsCLI provides components for system prompt."""
        skills_dir = tmp_path / ".skills"
        skill_dir = skills_dir / "skill-a"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: Skill A
description: First skill
---

Instructions A
""")
        cli = SkillsCLI(skills_dir=skills_dir)
        cli.discover()
        cli.load("skill-a")

        metadata_prompt = cli.get_skills_metadata_prompt()
        loaded_prompt = cli.get_loaded_skills_prompt()

        assert "skill-a" in metadata_prompt
        assert "Skill A" in metadata_prompt
        assert "# Skill: skill-a" in loaded_prompt
        assert "Instructions A" in loaded_prompt
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/skills/test_cli.py -v`
Expected: FAIL with ModuleNotFoundError: No module named 'skills.cli'

**Step 3: Write minimal implementation**

```python
# src/skills/cli.py
"""CLI integration for the skills system."""

from pathlib import Path

from skills.context import SkillsContext
from skills.discovery import discover_skills
from skills.models import SkillMetadata
from skills.tool import SkillToolResult, skill_tool


class SkillsCLI:
    """High-level interface for skills system integration.

    Provides a simple API for CLI applications to:
    - Discover available skills
    - List skill metadata
    - Load skills on demand
    - Generate prompt components
    """

    def __init__(self, skills_dir: Path | str | None = None):
        """Initialize the skills CLI.

        Args:
            skills_dir: Path to the skills directory. Defaults to ./.skills
        """
        self._skills_dir = Path(skills_dir) if skills_dir else Path(".skills")
        self._context = SkillsContext(skills_dir=self._skills_dir)
        self._discovery_errors: list[str] = []

    @property
    def context(self) -> SkillsContext:
        """Get the underlying skills context."""
        return self._context

    @property
    def discovery_errors(self) -> list[str]:
        """Get any errors from the last discovery."""
        return self._discovery_errors

    def discover(self) -> int:
        """Discover all skills in the skills directory.

        Returns:
            Number of skills discovered.
        """
        result = discover_skills(self._skills_dir)
        self._context.set_discovered_skills(result.skills)
        self._discovery_errors = result.errors
        return len(result.skills)

    def list_skills(self) -> list[SkillMetadata]:
        """List all discovered skills.

        Returns:
            List of skill metadata.
        """
        return self._context.get_all_metadata()

    def load(self, skill_id: str) -> SkillToolResult:
        """Load a skill by ID.

        Args:
            skill_id: The skill identifier to load.

        Returns:
            SkillToolResult indicating success or failure.
        """
        return skill_tool(skill_id, self._context)

    def unload(self, skill_id: str) -> bool:
        """Unload a skill.

        Args:
            skill_id: The skill identifier to unload.

        Returns:
            True if unloaded, False if wasn't loaded.
        """
        return self._context.unload_skill(skill_id)

    def get_skills_metadata_prompt(self) -> str:
        """Get formatted skill metadata for system prompt.

        Returns:
            Formatted string with all skill metadata.
        """
        return self._context.format_metadata_for_prompt()

    def get_loaded_skills_prompt(self) -> str:
        """Get formatted loaded skills for system prompt.

        Returns:
            Formatted string with loaded skill content.
        """
        return self._context.format_loaded_skills()

    def is_loaded(self, skill_id: str) -> bool:
        """Check if a skill is loaded.

        Args:
            skill_id: The skill identifier to check.

        Returns:
            True if loaded, False otherwise.
        """
        return self._context.is_skill_loaded(skill_id)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/skills/test_cli.py -v`
Expected: PASS (all 5 tests)

**Step 5: Commit**

```bash
git add src/skills/cli.py tests/skills/test_cli.py
git commit -m "feat: add CLI integration for skills system"
```

---

## Task 8: Update Package Init

**Files:**
- Modify: `src/skills/__init__.py`

**Step 1: Update exports**

```python
# src/skills/__init__.py
"""Python Skills System - Enable AI agents to discover and load skill definitions."""

from skills.models import Skill, SkillMetadata, SkillDiscoveryResult
from skills.discovery import discover_skills, derive_skill_id
from skills.loader import load_skill, parse_frontmatter
from skills.context import SkillsContext
from skills.tool import skill_tool, SkillToolResult
from skills.cli import SkillsCLI

__version__ = "0.1.0"

__all__ = [
    # Models
    "Skill",
    "SkillMetadata",
    "SkillDiscoveryResult",
    # Discovery
    "discover_skills",
    "derive_skill_id",
    # Loader
    "load_skill",
    "parse_frontmatter",
    # Context
    "SkillsContext",
    # Tool
    "skill_tool",
    "SkillToolResult",
    # CLI
    "SkillsCLI",
]
```

**Step 2: Run all tests**

Run: `pytest tests/ -v --cov=skills`
Expected: PASS (all tests, good coverage)

**Step 3: Commit**

```bash
git add src/skills/__init__.py
git commit -m "feat: update package exports"
```

---

## Task 9: Create Example Skill

**Files:**
- Create: `.skills/example/SKILL.md`

**Step 1: Create example skill**

```markdown
# .skills/example/SKILL.md
---
name: Example Skill
description: An example skill demonstrating the skill file format and structure
category: documentation
tags:
  - example
  - template
  - documentation
---

# Example Skill

This is an example skill that demonstrates the proper structure and format for skill files.

## When to Use

Use this skill as a reference when creating new skills.

## Structure

A skill file consists of:

1. **Frontmatter** (YAML between `---` delimiters)
   - `name`: Human-readable name (required)
   - `description`: When and how to use (required)
   - `category`: Organizational category (optional)
   - `tags`: List of tags for filtering (optional)

2. **Body** (Markdown content)
   - Detailed instructions
   - Usage examples
   - Best practices

## Example Usage

```python
from skills import SkillsCLI

cli = SkillsCLI()
cli.discover()
result = cli.load("example")
print(result.content)
```
```

**Step 2: Commit**

```bash
git add .skills/
git commit -m "docs: add example skill"
```

---

## Task 10: Integration Test

**Files:**
- Create: `tests/skills/test_integration.py`

**Step 1: Write integration test**

```python
# tests/skills/test_integration.py
"""Integration tests for the complete skills system."""

import pytest
from pathlib import Path
from skills import SkillsCLI, SkillMetadata


class TestSkillsSystemIntegration:
    """End-to-end tests for the skills system."""

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """Create a skills directory with multiple skills."""
        skills_path = tmp_path / ".skills"

        # Create simple skill
        simple = skills_path / "simple"
        simple.mkdir(parents=True)
        (simple / "SKILL.md").write_text("""---
name: Simple Skill
description: A basic skill for testing
---

# Simple Instructions

Just do the simple thing.
""")

        # Create nested skill
        nested = skills_path / "category" / "nested"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("""---
name: Nested Skill
description: A nested skill with hierarchy
category: testing
tags:
  - nested
  - test
---

# Nested Instructions

Do the nested thing.
""")

        # Create skill with resources (directory structure only)
        with_resources = skills_path / "with-resources"
        with_resources.mkdir(parents=True)
        (with_resources / "SKILL.md").write_text("""---
name: Resource Skill
description: A skill with bundled resources
---

# Using Resources

Check the scripts/ directory for helpers.
""")
        (with_resources / "scripts").mkdir()
        (with_resources / "scripts" / "helper.py").write_text("print('helper')")

        return skills_path

    def test_full_workflow(self, skills_dir: Path):
        """Test complete discovery → list → load → unload workflow."""
        # Initialize
        cli = SkillsCLI(skills_dir=skills_dir)

        # Discover
        count = cli.discover()
        assert count == 3
        assert len(cli.discovery_errors) == 0

        # List
        skills = cli.list_skills()
        assert len(skills) == 3
        skill_ids = {s.id for s in skills}
        assert "simple" in skill_ids
        assert "category/nested" in skill_ids
        assert "with-resources" in skill_ids

        # Check metadata prompt
        metadata_prompt = cli.get_skills_metadata_prompt()
        assert "Simple Skill" in metadata_prompt
        assert "Nested Skill" in metadata_prompt

        # Load skills
        result1 = cli.load("simple")
        assert result1.success is True
        assert "# Simple Instructions" in result1.content

        result2 = cli.load("category/nested")
        assert result2.success is True
        assert "# Nested Instructions" in result2.content

        # Check loaded prompt
        loaded_prompt = cli.get_loaded_skills_prompt()
        assert "# Skill: simple" in loaded_prompt
        assert "# Skill: category/nested" in loaded_prompt
        assert "---" in loaded_prompt  # Separator

        # Verify loaded state
        assert cli.is_loaded("simple") is True
        assert cli.is_loaded("category/nested") is True
        assert cli.is_loaded("with-resources") is False

        # Unload
        assert cli.unload("simple") is True
        assert cli.is_loaded("simple") is False

        # Verify unloaded
        loaded_prompt = cli.get_loaded_skills_prompt()
        assert "# Skill: simple" not in loaded_prompt
        assert "# Skill: category/nested" in loaded_prompt

    def test_load_already_loaded_skill(self, skills_dir: Path):
        """Test that loading an already-loaded skill returns cached version."""
        cli = SkillsCLI(skills_dir=skills_dir)
        cli.discover()

        # Load twice
        result1 = cli.load("simple")
        result2 = cli.load("simple")

        assert result1.success is True
        assert result2.success is True
        assert result2.already_loaded is True

    def test_load_nonexistent_skill(self, skills_dir: Path):
        """Test that loading unknown skill returns error."""
        cli = SkillsCLI(skills_dir=skills_dir)
        cli.discover()

        result = cli.load("nonexistent")

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_empty_skills_directory(self, tmp_path: Path):
        """Test behavior with empty skills directory."""
        empty_dir = tmp_path / ".skills"
        empty_dir.mkdir()

        cli = SkillsCLI(skills_dir=empty_dir)
        count = cli.discover()

        assert count == 0
        assert cli.list_skills() == []
        assert cli.get_skills_metadata_prompt() == "No skills available."
        assert cli.get_loaded_skills_prompt() == "[CURRENTLY EMPTY]"
```

**Step 2: Run integration tests**

Run: `pytest tests/skills/test_integration.py -v`
Expected: PASS (all 4 tests)

**Step 3: Run full test suite with coverage**

Run: `pytest tests/ -v --cov=skills --cov-report=term-missing`
Expected: PASS with >90% coverage

**Step 4: Commit**

```bash
git add tests/skills/test_integration.py
git commit -m "test: add integration tests for skills system"
```

---

## Task 11: Create Skill Creator Meta-Skill

**Files:**
- Create: `.skills/skill-creator/SKILL.md`
- Create: `.skills/skill-creator/scripts/init_skill.py`

**Step 1: Create skill-creator SKILL.md**

```markdown
# .skills/skill-creator/SKILL.md
---
name: Skill Creator
description: Use this skill when creating new skills. Guides the design and implementation of skill files.
category: meta
tags:
  - skill-creation
  - meta
  - templates
---

# Skill Creator

A meta-skill for creating new skills in the Python skills system.

## Skill Design Principles

### 1. Clear Purpose
- Each skill should do ONE thing well
- The description should make it immediately clear when to use the skill
- Avoid overlapping functionality with existing skills

### 2. Progressive Disclosure
- Metadata (frontmatter) provides quick identification
- Body provides full instructions
- Resources (scripts/, references/) provide extended functionality

### 3. Self-Contained
- Skills should work independently
- Include all necessary context in the skill body
- Reference external resources only when necessary

## Creating a New Skill

### Step 1: Plan the Skill
1. Define the skill's purpose
2. Determine when it should be used
3. Identify required resources (if any)

### Step 2: Create the Directory
```bash
python .skills/skill-creator/scripts/init_skill.py <skill-name>
```

### Step 3: Write the Frontmatter
Required fields:
- `name`: Human-readable title
- `description`: When and how to use (this triggers skill loading!)

Optional fields:
- `category`: Organizational grouping
- `tags`: Keywords for filtering

### Step 4: Write the Body
- Start with a clear heading
- Explain when to use the skill
- Provide step-by-step instructions
- Include examples

### Step 5: Add Resources (Optional)
- `scripts/`: Executable helpers
- `references/`: Documentation
- `assets/`: Templates, images

## Skill File Template

```markdown
---
name: [Skill Name]
description: [When to use this skill - be specific!]
category: [optional]
tags: [optional]
---

# [Skill Name]

[Brief overview]

## When to Use

[Specific triggers for using this skill]

## Instructions

[Step-by-step guidance]

## Examples

[Concrete examples]
```
```

**Step 2: Create init_skill.py helper**

```python
#!/usr/bin/env python3
# .skills/skill-creator/scripts/init_skill.py
"""Initialize a new skill directory with template files."""

import argparse
import sys
from pathlib import Path


SKILL_TEMPLATE = '''---
name: {name}
description: TODO - Describe when to use this skill
category:
tags: []
---

# {name}

TODO - Add skill overview.

## When to Use

TODO - Describe specific triggers for using this skill.

## Instructions

TODO - Add step-by-step guidance.

## Examples

TODO - Add concrete examples.
'''


def init_skill(skill_name: str, base_path: Path | None = None) -> Path:
    """Initialize a new skill directory.

    Args:
        skill_name: Name/ID of the skill (used for directory name).
        base_path: Base path for .skills directory. Defaults to current directory.

    Returns:
        Path to the created skill directory.
    """
    if base_path is None:
        base_path = Path.cwd()

    skills_dir = base_path / ".skills"
    skill_dir = skills_dir / skill_name

    if skill_dir.exists():
        raise ValueError(f"Skill directory already exists: {skill_dir}")

    # Create directories
    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()
    (skill_dir / "assets").mkdir()

    # Create SKILL.md
    skill_file = skill_dir / "SKILL.md"
    human_name = skill_name.replace("-", " ").replace("_", " ").title()
    skill_file.write_text(SKILL_TEMPLATE.format(name=human_name))

    # Create placeholder files
    (skill_dir / "scripts" / ".gitkeep").touch()
    (skill_dir / "references" / ".gitkeep").touch()
    (skill_dir / "assets" / ".gitkeep").touch()

    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Initialize a new skill")
    parser.add_argument("name", help="Skill name/ID (e.g., 'my-skill' or 'category/skill')")
    parser.add_argument("--path", type=Path, help="Base path (default: current directory)")

    args = parser.parse_args()

    try:
        skill_dir = init_skill(args.name, args.path)
        print(f"Created skill at: {skill_dir}")
        print(f"Edit {skill_dir / 'SKILL.md'} to define your skill.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 3: Commit**

```bash
git add .skills/skill-creator/
git commit -m "feat: add skill-creator meta-skill"
```

---

## Summary

This plan implements a complete Python skills system with:

| Component | File | Purpose |
|-----------|------|---------|
| Models | `src/skills/models.py` | Pydantic data models |
| Loader | `src/skills/loader.py` | Frontmatter parsing |
| Discovery | `src/skills/discovery.py` | Recursive skill scanning |
| Context | `src/skills/context.py` | Two-tier memory management |
| Tool | `src/skills/tool.py` | Skill loading on demand |
| CLI | `src/skills/cli.py` | High-level integration API |

**Key Design Decisions:**
1. Two-tier memory (metadata always loaded, content on-demand)
2. Filesystem-based persistence (no database)
3. Hierarchical skill IDs from directory structure
4. Pydantic for validation and type safety
5. Full test coverage with TDD approach

**Total: 11 tasks, ~40 steps**

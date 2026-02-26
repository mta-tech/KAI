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
from app.modules.skill.services import SkillService

service = SkillService(storage)
skill = service.get_skill_by_skill_id(db_connection_id, "example")
print(skill.content)
```

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

A meta-skill for creating new skills in the KAI skills system.

## When to Use

Load this skill when:
- Creating a new analysis skill
- Defining reusable analysis patterns
- Documenting domain-specific knowledge
- Setting up skill templates for a new domain

## Skill Design Principles

### 1. Clear Purpose
- Each skill should do ONE thing well
- The description should make it immediately clear when to use the skill
- Avoid overlapping functionality with existing skills

### 2. Progressive Disclosure
- Frontmatter provides quick identification (name, description)
- Body provides full instructions
- Use clear headings for different sections

### 3. Actionable Content
- Include actual SQL templates that can be adapted
- Provide step-by-step workflows
- List common pitfalls to avoid

## Creating a New Skill

### Step 1: Plan the Skill
1. Define the skill's purpose
2. Determine when it should be used (trigger conditions)
3. Identify the key patterns/templates to include

### Step 2: Create the Directory
```bash
mkdir -p .skills/category/skill-name
```

### Step 3: Write the SKILL.md File

Required frontmatter:
- `name`: Human-readable title
- `description`: When and how to use (this triggers skill loading!)

Optional frontmatter:
- `category`: Organizational grouping
- `tags`: Keywords for filtering

### Step 4: Write the Body
- Start with a clear heading
- Explain when to use the skill
- Provide SQL templates with comments
- Include a step-by-step workflow
- List best practices and pitfalls

### Step 5: Register the Skill
```bash
kai-agent discover-skills <connection_id> --path ./.skills
```

## Skill File Template

```markdown
---
name: [Skill Name]
description: [When to use this skill - be specific!]
category: [category]
tags:
  - [tag1]
  - [tag2]
---

# [Skill Name]

[Brief overview of what this skill helps with]

## When to Use

[Specific triggers for using this skill]

## Standard Queries/Patterns

[SQL templates with placeholders and comments]

## Workflow

[Step-by-step process for analysis]

## Best Practices

[Key recommendations]

## Common Pitfalls

[Things to avoid]
```

## Naming Conventions

- Use lowercase with hyphens for skill IDs: `revenue-analysis`, `data-quality`
- Use clear, descriptive names: "Revenue Analysis" not "Rev Anal"
- Categories should be broad: `analysis`, `meta`, `reporting`
- Tags should be specific: `revenue`, `financial`, `sql-patterns`

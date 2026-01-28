"""Knowledge management commands (glossary, instructions, skills, memory)."""

import json
import click
from rich.panel import Panel

from app.modules.autonomous_agent.cli import console, ensure_typesense_or_prompt


@click.group()
def knowledge():
    """Knowledge management commands (glossary, instructions, skills, memory).

    These commands manage knowledge artifacts that enhance the AI agent's
    understanding of your business domain and data.
    """
    pass


@click.group()
def glossary():
    """Business glossary management.

    Business glossary entries define business metrics and their SQL calculations.
    The agent uses these to understand business terminology when answering questions.
    """
    pass


@glossary.command("add")
@click.argument("db_connection_id")
@click.option("--metric", "-m", required=True, help="Business metric name")
@click.option("--sql", "-s", required=True, help="SQL query for the metric")
@click.option("--alias", "-a", "aliases", multiple=True, help="Alternative names for this metric (can specify multiple)")
@click.option("--metadata", type=str, help="JSON metadata for the glossary entry")
def add_glossary(db_connection_id: str, metric: str, sql: str, aliases: tuple, metadata: str):
    """Add a new business glossary entry.

    Business glossary entries define business metrics and their SQL calculations.
    The agent uses these to understand business terminology when answering questions.

    Examples:

        # Simple metric
        kai knowledge glossary add abc123 --metric "Revenue" --sql "SELECT SUM(amount) FROM orders"

        # Metric with aliases
        kai knowledge glossary add abc123 -m "MRR" -s "SELECT SUM(amount) FROM subscriptions WHERE status='active'" -a "Monthly Recurring Revenue" -a "Recurring Revenue"

        # Metric with metadata
        kai knowledge glossary add abc123 -m "Churn Rate" -s "SELECT COUNT(*) FILTER (WHERE churned) * 100.0 / COUNT(*) FROM customers" --metadata '{"unit": "percentage", "category": "retention"}'
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import BusinessGlossaryRequest
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    request = BusinessGlossaryRequest(
        metric=metric,
        alias=list(aliases) if aliases else None,
        sql=sql,
        metadata=meta_dict,
    )

    console.print(f"[bold]Adding business glossary entry...[/bold]")
    console.print(f"[dim]Metric: {metric}[/dim]")
    console.print(f"[dim]SQL: {sql[:60]}...[/dim]" if len(sql) > 60 else f"[dim]SQL: {sql}[/dim]")

    try:
        glossary = service.create_business_glossary(db_connection_id, request)

        console.print(f"\n[green]✔ Glossary entry created successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {glossary.id}\n"
            f"[bold]Metric:[/bold] {glossary.metric}\n"
            f"[bold]Aliases:[/bold] {', '.join(glossary.alias) if glossary.alias else 'None'}\n"
            f"[bold]SQL:[/bold] {glossary.sql}\n"
            f"[bold]Created:[/bold] {glossary.created_at}",
            title="Business Glossary Entry",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to create glossary entry:[/red] {str(e)}")


@glossary.command("list")
@click.argument("db_connection_id")
@click.option("--verbose", "-v", is_flag=True, help="Show full SQL queries")
def list_glossaries(db_connection_id: str, verbose: bool):
    """List all business glossary entries for a connection.

    Examples:

        kai knowledge glossary list abc123

        kai knowledge glossary list abc123 --verbose
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    glossaries = service.get_business_glossaries(db_connection_id)

    if not glossaries:
        console.print("[yellow]No business glossary entries found[/yellow]")
        console.print(f"[dim]Add one with: kai knowledge glossary add {db_connection_id} -m 'Metric Name' -s 'SELECT ...'[/dim]")
        return

    console.print(f"[bold]Business Glossary ({len(glossaries)} entries):[/bold]\n")

    for g in glossaries:
        console.print(f"  [cyan]●[/cyan] [bold]{g.metric}[/bold]")
        console.print(f"      [dim]ID: {g.id}[/dim]")

        if g.alias:
            console.print(f"      [italic]Aliases: {', '.join(g.alias)}[/italic]")

        if verbose:
            console.print(f"      [dim]SQL: {g.sql}[/dim]")
        else:
            sql_preview = g.sql[:60] + "..." if len(g.sql) > 60 else g.sql
            console.print(f"      [dim]SQL: {sql_preview}[/dim]")

        if g.metadata:
            console.print(f"      [dim]Metadata: {g.metadata}[/dim]")

        console.print()


@glossary.command("show")
@click.argument("glossary_id")
def show_glossary(glossary_id: str):
    """Show details of a business glossary entry.

    Example:

        kai knowledge glossary show glossary_abc123
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    try:
        glossary = service.get_business_glossary(glossary_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    console.print(Panel(
        f"[bold]ID:[/bold] {glossary.id}\n"
        f"[bold]Metric:[/bold] {glossary.metric}\n"
        f"[bold]Aliases:[/bold] {', '.join(glossary.alias) if glossary.alias else 'None'}\n"
        f"[bold]Connection ID:[/bold] {glossary.db_connection_id}\n"
        f"[bold]Created:[/bold] {glossary.created_at}\n"
        f"[bold]Metadata:[/bold] {glossary.metadata or 'None'}",
        title=f"Business Glossary: {glossary.metric}",
        border_style="cyan"
    ))

    console.print(f"\n[bold]SQL Definition:[/bold]")
    console.print(Panel(glossary.sql, border_style="dim"))


@glossary.command("update")
@click.argument("glossary_id")
@click.option("--metric", "-m", help="New metric name")
@click.option("--sql", "-s", help="New SQL query")
@click.option("--alias", "-a", "aliases", multiple=True, help="New alias(es) - replaces existing")
@click.option("--metadata", type=str, help="New JSON metadata")
def update_glossary(glossary_id: str, metric: str, sql: str, aliases: tuple, metadata: str):
    """Update an existing business glossary entry.

    Examples:

        # Update SQL
        kai knowledge glossary update glossary_abc123 --sql "SELECT SUM(amount) FROM orders WHERE status='completed'"

        # Update metric name
        kai knowledge glossary update glossary_abc123 --metric "Total Revenue"

        # Update aliases
        kai knowledge glossary update glossary_abc123 -a "Gross Revenue" -a "Sales Revenue"
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import UpdateBusinessGlossaryRequest
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    # Check if glossary exists
    try:
        existing = service.get_business_glossary(glossary_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    # Build update request with only provided fields
    update_data = {}
    if metric:
        update_data["metric"] = metric
    if sql:
        update_data["sql"] = sql
    if aliases:
        update_data["alias"] = list(aliases)
    if meta_dict is not None:
        update_data["metadata"] = meta_dict

    if not update_data:
        console.print("[yellow]No updates provided[/yellow]")
        return

    request = UpdateBusinessGlossaryRequest(**update_data)

    console.print(f"[bold]Updating glossary entry '{existing.metric}'...[/bold]")

    try:
        updated = service.update_business_glossary(glossary_id, request)

        console.print(f"\n[green]✔ Glossary entry updated successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {updated.id}\n"
            f"[bold]Metric:[/bold] {updated.metric}\n"
            f"[bold]Aliases:[/bold] {', '.join(updated.alias) if updated.alias else 'None'}\n"
            f"[bold]SQL:[/bold] {updated.sql}",
            title="Updated Glossary Entry",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to update glossary entry:[/red] {str(e)}")


@glossary.command("delete")
@click.argument("glossary_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_glossary(glossary_id: str, force: bool):
    """Delete a business glossary entry.

    Examples:

        kai knowledge glossary delete glossary_abc123

        kai knowledge glossary delete glossary_abc123 --force
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.business_glossary.services import BusinessGlossaryService

    settings = Settings()
    storage = Storage(settings)
    service = BusinessGlossaryService(storage)

    # Check if glossary exists
    try:
        glossary = service.get_business_glossary(glossary_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    console.print(f"[bold]Glossary entry to delete:[/bold]")
    console.print(f"  ID: {glossary.id}")
    console.print(f"  Metric: {glossary.metric}")
    console.print(f"  SQL: {glossary.sql[:60]}..." if len(glossary.sql) > 60 else f"  SQL: {glossary.sql}")

    if not force:
        if not click.confirm("\nAre you sure you want to delete this glossary entry?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        service.delete_business_glossary(glossary_id)
        console.print(f"\n[green]✔ Glossary entry '{glossary.metric}' deleted successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete glossary entry:[/red] {str(e)}")


@click.group()
def instruction():
    """Business instruction management.

    Business instructions define rules and conditions for SQL generation.
    The agent uses these to apply business-specific constraints and logic.
    """
    pass


@instruction.command("add")
@click.argument("db_connection_id")
@click.option("--category", "-c", required=True, help="Instruction category/condition (when to apply)")
@click.option("--rule", "-r", required=True, help="Business rule to apply")
@click.option("--instruction", "-i", help="Additional instruction/description")
@click.option("--scope", "-s", help="Instruction scope (e.g., 'default' for is_default)")
@click.option("--metadata", type=str, help="JSON metadata for the instruction")
def add_instruction(db_connection_id: str, category: str, rule: str, instruction: str, scope: str, metadata: str):
    """Add a new business instruction.

    Business instructions define rules and conditions for SQL generation.
    The agent uses these to apply business-specific constraints and logic.

    Examples:

        # Simple instruction
        kai knowledge instruction add abc123 --category "Revenue queries" --rule "Always filter by active subscriptions"

        # Instruction with description
        kai knowledge instruction add abc123 -c "Time-based analysis" -r "Use last 30 days when no time range specified" -i "Default to recent data"

        # Default instruction (applies to all queries)
        kai knowledge instruction add abc123 -c "General" -r "Exclude test accounts" -s "default"
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import InstructionRequest
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    # Handle scope parameter
    is_default = False
    if scope and scope.lower() == "default":
        is_default = True

    # Combine rule and instruction if both provided
    rules_text = rule
    if instruction:
        rules_text = f"{rule}. {instruction}"

    request = InstructionRequest(
        db_connection_id=db_connection_id,
        condition=category,
        rules=rules_text,
        is_default=is_default,
        metadata=meta_dict,
    )

    console.print(f"[bold]Adding business instruction...[/bold]")
    console.print(f"[dim]Category: {category}[/dim]")
    console.print(f"[dim]Rule: {rule[:80]}...[/dim]" if len(rule) > 80 else f"[dim]Rule: {rule}[/dim]")

    try:
        instr = service.create_instruction(request)

        console.print(f"\n[green]✔ Instruction created successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {instr.id}\n"
            f"[bold]Category:[/bold] {instr.condition}\n"
            f"[bold]Rules:[/bold] {instr.rules[:100]}...[/dim]\n" if len(instr.rules) > 100 else f"[bold]Rules:[/bold] {instr.rules}\n"
            f"[bold]Is Default:[/bold] {instr.is_default}\n"
            f"[bold]Created:[/bold] {instr.created_at}",
            title="Business Instruction",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to create instruction:[/red] {str(e)}")


@instruction.command("list")
@click.argument("db_connection_id")
@click.option("--verbose", "-v", is_flag=True, help="Show full rule descriptions")
def list_instructions(db_connection_id: str, verbose: bool):
    """List all business instructions for a connection.

    Examples:

        kai knowledge instruction list abc123

        kai knowledge instruction list abc123 --verbose
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    instructions = service.get_instructions(db_connection_id)

    if not instructions:
        console.print("[yellow]No business instructions found[/yellow]")
        console.print(f"[dim]Add one with: kai knowledge instruction add {db_connection_id} -c 'Category' -r 'Rule'[/dim]")
        return

    console.print(f"[bold]Business Instructions ({len(instructions)} entries):[/bold]\n")

    for instr in instructions:
        default_tag = " [dim](default)[/dim]" if instr.is_default else ""
        console.print(f"  [cyan]●[/cyan] [bold]{instr.condition}[/bold]{default_tag}")
        console.print(f"      [dim]ID: {instr.id}[/dim]")

        if verbose:
            console.print(f"      [dim]Rules: {instr.rules}[/dim]")
        else:
            rules_preview = instr.rules[:80] + "..." if len(instr.rules) > 80 else instr.rules
            console.print(f"      [dim]Rules: {rules_preview}[/dim]")

        if instr.metadata:
            console.print(f"      [dim]Metadata: {instr.metadata}[/dim]")

        console.print()


@instruction.command("show")
@click.argument("instruction_id")
def show_instruction(instruction_id: str):
    """Show details of a business instruction.

    Example:

        kai knowledge instruction show instruction_abc123
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    try:
        instr = service.get_instruction(instruction_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    default_tag = "Yes" if instr.is_default else "No"

    console.print(Panel(
        f"[bold]ID:[/bold] {instr.id}\n"
        f"[bold]Category:[/bold] {instr.condition}\n"
        f"[bold]Connection ID:[/bold] {instr.db_connection_id}\n"
        f"[bold]Is Default:[/bold] {default_tag}\n"
        f"[bold]Created:[/bold] {instr.created_at}\n"
        f"[bold]Metadata:[/bold] {instr.metadata or 'None'}",
        title=f"Business Instruction: {instr.condition}",
        border_style="cyan"
    ))

    console.print(f"\n[bold]Rules:[/bold]")
    console.print(Panel(instr.rules, border_style="dim"))


@instruction.command("update")
@click.argument("instruction_id")
@click.option("--category", "-c", help="New category/condition")
@click.option("--rule", "-r", help="New rule")
@click.option("--instruction", "-i", help="New additional instruction/description")
@click.option("--scope", "-s", help="New scope (e.g., 'default' for is_default)")
@click.option("--metadata", type=str, help="New JSON metadata (replaces existing)")
def update_instruction(instruction_id: str, category: str, rule: str, instruction: str, scope: str, metadata: str):
    """Update an existing business instruction.

    Examples:

        # Update rule
        kai knowledge instruction update instruction_abc123 --rule "Always filter by active paid subscriptions"

        # Update category
        kai knowledge instruction update instruction_abc123 --category "Revenue queries - updated"

        # Set as default instruction
        kai knowledge instruction update instruction_abc123 --scope "default"
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.api.requests import UpdateInstructionRequest
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    # Check if instruction exists
    try:
        existing = service.get_instruction(instruction_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    # Parse metadata if provided
    meta_dict = None
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError:
            console.print("[red]Error:[/red] Invalid JSON in metadata")
            return

    # Build update request with only provided fields
    update_data = {}
    if category is not None:
        update_data["condition"] = category
    if rule is not None:
        # Combine with instruction if provided
        rules_text = rule
        if instruction:
            rules_text = f"{rule}. {instruction}"
        update_data["rules"] = rules_text
    elif instruction is not None:
        # Only instruction provided, append to existing rules
        update_data["rules"] = f"{existing.rules}. {instruction}"
    if scope is not None:
        update_data["is_default"] = scope.lower() == "default"
    if meta_dict is not None:
        update_data["metadata"] = meta_dict

    if not update_data:
        console.print("[yellow]No updates provided[/yellow]")
        return

    request = UpdateInstructionRequest(**update_data)

    console.print(f"[bold]Updating instruction '{existing.condition}'...[/bold]")

    try:
        updated = service.update_instruction(instruction_id, request)

        console.print(f"\n[green]✔ Instruction updated successfully![/green]")
        console.print(Panel(
            f"[bold]ID:[/bold] {updated.id}\n"
            f"[bold]Category:[/bold] {updated.condition}\n"
            f"[bold]Rules:[/bold] {updated.rules[:100]}...[/dim]\n" if len(updated.rules) > 100 else f"[bold]Rules:[/bold] {updated.rules}\n"
            f"[bold]Is Default:[/bold] {updated.is_default}",
            title="Updated Instruction",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to update instruction:[/red] {str(e)}")


@instruction.command("delete")
@click.argument("instruction_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_instruction(instruction_id: str, force: bool):
    """Delete a business instruction.

    Examples:

        kai knowledge instruction delete instruction_abc123

        kai knowledge instruction delete instruction_abc123 --force
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.instruction.services import InstructionService

    settings = Settings()
    storage = Storage(settings)
    service = InstructionService(storage)

    # Check if instruction exists
    try:
        instr = service.get_instruction(instruction_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    default_tag = " (default)" if instr.is_default else ""

    console.print(f"[bold]Instruction to delete:[/bold]")
    console.print(f"  ID: {instr.id}")
    console.print(f"  Category: {instr.condition}{default_tag}")
    console.print(f"  Rules: {instr.rules[:80]}..." if len(instr.rules) > 80 else f"  Rules: {instr.rules}")

    if not force:
        if not click.confirm("\nAre you sure you want to delete this instruction?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        service.delete_instruction(instruction_id)
        console.print(f"\n[green]✔ Instruction '{instr.condition}' deleted successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete instruction:[/red] {str(e)}")


@click.group()
def skill():
    """AI skill management - reusable analysis patterns."""
    pass


@skill.command("discover")
@click.argument("db_connection_id")
@click.option("--path", "-p", default="./.skills", help="Path to skills directory")
@click.option("--sync/--no-sync", "sync_to_storage", default=True, help="Sync discovered skills to storage")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def discover_skills(db_connection_id: str, path: str, sync_to_storage: bool, verbose: bool):
    """Discover and sync skills from a directory.

    Scans the specified directory (default: ./.skills) for SKILL.md files
    and syncs them to TypeSense storage.

    Examples:

        # Discover skills from default path
        kai knowledge skill discover abc123

        # Discover from custom path
        kai knowledge skill discover abc123 --path /path/to/skills

        # Preview without syncing
        kai knowledge skill discover abc123 --no-sync
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from pathlib import Path
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    skills_path = Path(path)
    console.print(f"[bold]Discovering skills in:[/bold] {skills_path.absolute()}")
    console.print(f"[dim]Sync to storage: {'Yes' if sync_to_storage else 'No (preview only)'}[/dim]")

    try:
        result = service.discover_skills(
            db_connection_id, skills_path, sync_to_storage=sync_to_storage
        )

        if result.total_found == 0:
            console.print("\n[yellow]No skills found[/yellow]")
            console.print(f"[dim]Expected SKILL.md files in subdirectories of {path}[/dim]")
            return

        console.print(f"\n[green]✔ Discovered {result.total_found} skill(s)[/green]")

        for skill in result.skills:
            status = "[green]active[/green]" if skill.is_active else "[dim]inactive[/dim]"
            console.print(f"  • [bold]{skill.skill_id}[/bold] ({skill.name}) {status}")
            console.print(f"    [dim]{skill.description}[/dim]")
            if verbose:
                console.print(f"    [dim]File: {skill.file_path}[/dim]")

        if result.total_errors > 0:
            console.print(f"\n[yellow]⚠ {result.total_errors} error(s):[/yellow]")
            for error in result.errors:
                console.print(f"  [red]✖[/red] {error}")

    except Exception as e:
        console.print(f"\n[red]✖ Discovery failed:[/red] {str(e)}")


@skill.command("list")
@click.argument("db_connection_id")
@click.option("--active-only", "-a", is_flag=True, help="Show only active skills")
@click.option("--category", "-c", help="Filter by category")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def list_skills(db_connection_id: str, active_only: bool, category: str, verbose: bool):
    """List all skills for a database connection.

    Examples:

        kai knowledge skill list abc123

        kai knowledge skill list abc123 --active-only

        kai knowledge skill list abc123 --category analysis
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    if active_only:
        skills = service.get_active_skills(db_connection_id)
    else:
        skills = service.get_skills(db_connection_id)

    # Filter by category if specified
    if category:
        skills = [s for s in skills if s.category == category]

    if not skills:
        console.print("[yellow]No skills found[/yellow]")
        console.print(f"[dim]Discover skills with: kai knowledge skill discover {db_connection_id}[/dim]")
        return

    console.print(f"[bold]Skills ({len(skills)} total):[/bold]\n")

    # Group by category
    by_category: dict = {}
    for skill in skills:
        cat = skill.category or "uncategorized"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    for cat, cat_skills in sorted(by_category.items()):
        console.print(f"[cyan]{cat.upper()}[/cyan]")
        for skill in cat_skills:
            status = "[green]●[/green]" if skill.is_active else "[dim]○[/dim]"
            tags_str = f" [dim]({', '.join(skill.tags)})[/dim]" if skill.tags else ""
            console.print(f"  {status} [bold]{skill.skill_id}[/bold]: {skill.name}{tags_str}")
            desc = skill.description[:80] + "..." if len(skill.description) > 80 else skill.description
            console.print(f"      [dim]{desc}[/dim]")
            if verbose:
                console.print(f"      [dim]File: {skill.file_path}[/dim]")
        console.print()


@skill.command("show")
@click.argument("skill_id")
@click.option("--content", "-c", is_flag=True, help="Show full content")
def show_skill(skill_id: str, content: bool):
    """Show details of a specific skill.

    Example:

        kai knowledge skill show analysis/revenue

        kai knowledge skill show data-quality --content
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    try:
        # Need to extract db_connection_id from skill_id or ask user
        # For now, we'll search across all connections
        console.print("[yellow]Warning:[/yellow] This command requires knowing the database connection ID.")
        console.print("[dim]Please use 'kai knowledge skill list <db_connection_id>' to find skills.[/dim]")
        console.print("[dim]Alternatively, use the search command to find skills.[/dim]")
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return


@skill.command("search")
@click.argument("query")
@click.option("--db-connection-id", "-d", help="Database connection ID (optional)")
@click.option("--limit", "-l", default=5, help="Maximum number of results")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def search_skills(query: str, db_connection_id: str, limit: int, verbose: bool):
    """Search for skills by keyword or description.

    Uses semantic search to find relevant skills.

    Examples:

        kai knowledge skill search "revenue analysis"

        kai knowledge skill search "data quality" --limit 10

        kai knowledge skill search "revenue" -d abc123
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    if not db_connection_id:
        console.print("[yellow]Warning:[/yellow] Searching across all connections may be slow.")
        console.print("[dim]Specify --db-connection-id for faster results.[/dim]")
        return

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    console.print(f"[bold]Searching for:[/bold] {query}")

    try:
        skills = service.find_relevant_skills(db_connection_id, query, limit=limit)

        if not skills:
            console.print("\n[yellow]No skills found matching your query[/yellow]")
            console.print("[dim]Try different keywords or use list to see all available[/dim]")
            return

        console.print(f"\n[green]Found {len(skills)} skill(s):[/green]\n")

        for i, skill in enumerate(skills, 1):
            status = "[green]●[/green]" if skill.is_active else "[dim]○[/dim]"
            console.print(f"{i}. {status} [bold]{skill.skill_id}[/bold]: {skill.name}")
            console.print(f"   [dim]{skill.description}[/dim]")
            if verbose:
                console.print(f"   [dim]Category: {skill.category or 'None'}[/dim]")
                console.print(f"   [dim]Tags: {', '.join(skill.tags) if skill.tags else 'None'}[/dim]")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@skill.command("reload")
@click.argument("skill_id")
@click.option("--db-connection-id", "-d", required=True, help="Database connection ID")
@click.option("--path", "-p", default="./.skills", help="Path to skills directory")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def reload_skill(skill_id: str, db_connection_id: str, path: str, verbose: bool):
    """Reload a skill from its file.

    Use this after modifying a SKILL.md file to sync changes to storage.

    Examples:

        kai knowledge skill reload analysis/revenue -d abc123

        kai knowledge skill reload data-quality -d abc123 --path /custom/path
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from pathlib import Path
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    skills_path = Path(path)
    console.print(f"[bold]Reloading skill:[/bold] {skill_id}")
    console.print(f"[dim]From: {skills_path.absolute()}/{skill_id}/SKILL.md[/dim]")

    try:
        skill = service.reload_skill_from_file(db_connection_id, skill_id, skills_path)

        console.print(f"\n[green]✔ Skill reloaded successfully![/green]")
        console.print(Panel(
            f"[bold]Skill ID:[/bold] {skill.skill_id}\n"
            f"[bold]Name:[/bold] {skill.name}\n"
            f"[bold]Description:[/bold] {skill.description}\n"
            f"[bold]Updated:[/bold] {skill.updated_at}",
            title="Reloaded Skill",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]✖ Failed to reload skill:[/red] {str(e)}")


@skill.command("delete")
@click.argument("skill_id")
@click.option("--db-connection-id", "-d", required=True, help="Database connection ID")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def delete_skill(skill_id: str, db_connection_id: str, force: bool):
    """Delete a skill from storage.

    This removes the skill from TypeSense storage. The SKILL.md file is not deleted.

    Examples:

        kai knowledge skill delete analysis/revenue -d abc123

        kai knowledge skill delete data-quality -d abc123 --force
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.skill.services import SkillService

    settings = Settings()
    storage = Storage(settings)
    service = SkillService(storage)

    try:
        skill = service.get_skill_by_skill_id(db_connection_id, skill_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return

    console.print(f"[bold]Skill to delete:[/bold]")
    console.print(f"  ID: {skill.skill_id}")
    console.print(f"  Name: {skill.name}")
    console.print(f"  Category: {skill.category or 'None'}")

    if not force:
        console.print("\n[dim]Note: This only removes the skill from storage.")
        console.print("The SKILL.md file will not be deleted.[/dim]")
        if not click.confirm("\nAre you sure you want to delete this skill?"):
            console.print("[dim]Cancelled[/dim]")
            return

    try:
        service.delete_skill(db_connection_id, skill_id)
        console.print(f"\n[green]✔ Skill deleted successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]✖ Failed to delete skill:[/red] {str(e)}")


# Register glossary sub-group under knowledge
knowledge.add_command(glossary)

# Register instruction sub-group under knowledge
knowledge.add_command(instruction)

# Register skill sub-group under knowledge
knowledge.add_command(skill)

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


# Register glossary sub-group under knowledge
knowledge.add_command(glossary)

# Register instruction sub-group under knowledge
knowledge.add_command(instruction)

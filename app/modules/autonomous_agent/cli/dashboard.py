"""Dashboard management commands.

This command group contains commands for creating, listing, showing, executing,
rendering, deleting, and refining dashboards.
"""

import asyncio
import click
from rich.panel import Panel
from rich.table import Table

from app.modules.autonomous_agent.cli import console, ensure_typesense_or_prompt, _run_async


@click.group()
def dashboard():
    """Dashboard management commands.

    These commands handle creating, listing, executing, rendering,
    deleting, and refining dashboards for the KAI system.
    """
    pass


@dashboard.command("create")
@click.argument("request")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option("--name", help="Dashboard name (optional, auto-generated if not provided)")
@click.option("--theme", type=click.Choice(["default", "light", "dark", "ocean", "sunset", "forest"]), default="default", help="Dashboard theme")
def create_dashboard(request: str, db_connection_id: str, name: str | None, theme: str):
    """Create a dashboard from natural language.

    REQUEST: Natural language description of the dashboard

    Examples:

        kai-agent dashboard create "Sales dashboard with revenue trends and top products" --db sales_db

        kai-agent dashboard create "Customer analytics with churn metrics" --db crm --name "Customer 360"

        kai-agent dashboard create "Executive KPI dashboard" --db prod --theme ocean
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService
    from app.modules.dashboard.models import CreateDashboardRequest

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    create_request = CreateDashboardRequest(
        request=request,
        db_connection_id=db_connection_id,
        name=name,
        theme=theme
    )

    console.print(f"[bold]Creating dashboard...[/bold]")
    console.print(f"[dim]Request: {request[:100]}{'...' if len(request) > 100 else ''}[/dim]")

    try:
        with console.status("[bold cyan]Generating dashboard...[/bold cyan]"):
            dashboard = asyncio.run(service.create_from_nl(create_request))

        console.print(Panel(
            f"[bold green]✔ Dashboard created successfully![/bold green]\n\n"
            f"[cyan]ID:[/cyan] {dashboard.id}\n"
            f"[cyan]Name:[/cyan] {dashboard.name}\n"
            f"[cyan]Widgets:[/cyan] {len(dashboard.layout.widgets)}\n"
            f"[cyan]Theme:[/cyan] {dashboard.theme}\n\n"
            f"[dim]View dashboard: http://localhost:8015/dashboards/{dashboard.id}[/dim]",
            title="Dashboard Created",
            border_style="green"
        ))

        # Show widgets
        console.print("\n[bold]Widgets:[/bold]")
        for widget in dashboard.layout.widgets:
            console.print(f"  • [cyan]{widget.widget_type.value}[/cyan]: {widget.name}")

    except Exception as e:
        console.print(f"[red]Error creating dashboard:[/red] {e}")
        raise click.Abort()


@dashboard.command("list")
@click.option("--db", "db_connection_id", required=True, help="Database connection ID")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed dashboard info")
def list_dashboards(db_connection_id: str, verbose: bool):
    """List all dashboards for a database connection.

    Examples:

        kai-agent dashboard list --db sales_db

        kai-agent dashboard list --db prod -v
    """
    # Check Typesense first
    if not ensure_typesense_or_prompt(required=True):
        return

    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    dashboards = service.list_by_connection(db_connection_id)

    if not dashboards:
        console.print("[yellow]No dashboards found[/yellow]")
        return

    if verbose:
        console.print(f"[bold]Found {len(dashboards)} dashboard(s)[/bold]\n")

    table = Table(title=f"Dashboards ({len(dashboards)})")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Widgets")
    table.add_column("Theme")
    table.add_column("Created")

    if verbose:
        table.add_column("Description", style="dim")

    for dash in dashboards:
        row = [
            dash.id[:20] + "..." if len(dash.id) > 20 else dash.id,
            dash.name,
            str(len(dash.layout.widgets)),
            dash.theme,
            dash.created_at.strftime("%Y-%m-%d") if hasattr(dash.created_at, 'strftime') else str(dash.created_at)[:10]
        ]

        if verbose:
            row.append(dash.description or "N/A")

        table.add_row(*row)

    console.print(table)


@dashboard.command("show")
@click.argument("dashboard_id")
def show_dashboard(dashboard_id: str):
    """Show detailed information about a dashboard.

    Examples:

        kai-agent dashboard show abc123def456
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    dashboard = service.get(dashboard_id)

    if not dashboard:
        console.print(f"[red]Dashboard not found:[/red] {dashboard_id}")
        return

    # Dashboard info
    info = (
        f"[bold]ID:[/bold] {dashboard.id}\n"
        f"[bold]Name:[/bold] {dashboard.name}\n"
        f"[bold]Description:[/bold] {dashboard.description or 'N/A'}\n"
        f"[bold]Theme:[/bold] {dashboard.theme}\n"
        f"[bold]Widgets:[/bold] {len(dashboard.layout.widgets)}\n"
        f"[bold]Created:[/bold] {dashboard.created_at}\n"
        f"[bold]Updated:[/bold] {dashboard.updated_at}"
    )

    console.print(Panel(info, title=f"Dashboard: {dashboard.name}", border_style="cyan"))

    # Show widgets table
    widget_table = Table(title="Widgets")
    widget_table.add_column("Type")
    widget_table.add_column("Title")
    widget_table.add_column("Position")
    widget_table.add_column("Size")

    for widget in dashboard.layout.widgets:
        widget_table.add_row(
            widget.widget_type.value,
            widget.name,
            f"({widget.row}, {widget.col})",
            f"{widget.col_span}×{widget.row_span}"
        )

    console.print(widget_table)


@dashboard.command("execute")
@click.argument("dashboard_id")
@click.option("--save", "-s", is_flag=True, help="Save execution results")
@click.option("--output-format", type=click.Choice(["markdown", "json"]), default="markdown", help="Output format")
def execute_dashboard(dashboard_id: str, save: bool, output_format: str):
    """Execute all widgets in a dashboard (run queries).

    Examples:

        kai-agent dashboard execute abc123def456

        kai-agent dashboard execute abc123def456 --save

        kai-agent dashboard execute abc123def456 --output-format json
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    try:
        with console.status("[bold cyan]Executing dashboard...[/bold cyan]"):
            run = asyncio.run(service.execute(dashboard_id))

        console.print(f"[green]✔ Dashboard executed successfully![/green]")
        console.print(f"[dim]Execution time: {run.total_execution_time_ms}ms[/dim]")
        console.print(f"[dim]Widgets executed: {len(run.widget_results)}/{len(run.widget_results)}[/dim]")

        # Show any errors
        errors = [r for r in run.widget_results.values() if r.error]
        if errors:
            console.print(f"\n[yellow]Warnings: {len(errors)} widget(s) had errors[/yellow]")
            for err in errors[:3]:
                console.print(f"  [dim]• {err.widget_id}: {err.error}[/dim]")

        # Optionally save results
        if save:
            import json
            from pathlib import Path

            output_file = f"dashboard_run_{dashboard_id[:8]}.{output_format}"

            if output_format == "json":
                content = json.dumps({
                    "dashboard_id": dashboard_id,
                    "executed_at": str(run.executed_at),
                    "total_execution_time_ms": run.total_execution_time_ms,
                    "widget_results": {k: v.model_dump() for k, v in run.widget_results.items()}
                }, indent=2, default=str)
            else:
                lines = [
                    f"# Dashboard Execution Report",
                    f"",
                    f"**Dashboard ID:** {dashboard_id}",
                    f"**Executed At:** {run.executed_at}",
                    f"**Execution Time:** {run.total_execution_time_ms}ms",
                    f"",
                    f"## Widget Results",
                    f""
                ]
                for widget_id, result in run.widget_results.items():
                    status_emoji = "✔" if result.status == "completed" else "✖"
                    lines.append(f"### {status_emoji} {widget_id}")
                    lines.append(f"- Status: {result.status}")
                    lines.append(f"- Row Count: {result.row_count}")
                    if result.error:
                        lines.append(f"- Error: {result.error}")
                    lines.append(f"")

                content = "\n".join(lines)

            path = Path(output_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            console.print(f"[green]✔ Results saved to:[/green] {output_file}")

    except Exception as e:
        console.print(f"[red]Error executing dashboard:[/red] {e}")
        raise click.Abort()


@dashboard.command("render")
@click.argument("dashboard_id")
@click.option("--format", "-f", type=click.Choice(["html", "json"]), default="html", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Save to file")
@click.option("--execute/--no-execute", default=True, help="Execute queries before rendering")
def render_dashboard(dashboard_id: str, format: str, output: str, execute: bool):
    """Render a dashboard to HTML or JSON.

    Examples:

        kai-agent dashboard render abc123def456 --format html

        kai-agent dashboard render abc123def456 --format json -o dashboard.json

        kai-agent dashboard render abc123def456 --format html -o report.html --execute
    """
    from pathlib import Path
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    try:
        with console.status("[bold cyan]Rendering dashboard...[/bold cyan]"):
            result = asyncio.run(service.render(dashboard_id, execute_queries=execute))

        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(result)
            console.print(f"[green]✔ Dashboard saved to:[/green] {output}")
        else:
            if format == "json":
                console.print(result)
            else:
                console.print(f"[green]✔ Dashboard rendered ({len(result)} bytes)[/green]")
                console.print(f"[dim]Use --output to save to file[/dim]")

    except Exception as e:
        console.print(f"[red]Error rendering dashboard:[/red] {e}")
        raise click.Abort()


@dashboard.command("delete")
@click.argument("dashboard_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete_dashboard(dashboard_id: str, force: bool):
    """Delete a dashboard.

    Examples:

        kai-agent dashboard delete abc123def456

        kai-agent dashboard delete abc123def456 -f
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    # Get dashboard for confirmation
    dashboard = service.get(dashboard_id)
    if not dashboard:
        console.print(f"[red]Dashboard not found:[/red] {dashboard_id}")
        return

    if not force:
        console.print(f"[yellow]About to delete dashboard:[/yellow]")
        console.print(f"  Name: {dashboard.name}")
        console.print(f"  ID: {dashboard_id}")
        if not click.confirm("\nDo you want to continue?"):
            console.print("[dim]Cancelled[/dim]")
            return

    if service.delete(dashboard_id):
        console.print(f"[green]✔ Dashboard deleted:[/green] {dashboard.name}")
    else:
        console.print(f"[red]Failed to delete dashboard[/red]")


@dashboard.command("refine")
@click.argument("dashboard_id")
@click.argument("request")
def refine_dashboard(dashboard_id: str, request: str):
    """Refine a dashboard using natural language.

    Examples:

        kai-agent dashboard refine abc123def456 "Add a chart showing monthly revenue"

        kai-agent dashboard refine abc123def456 "Change the color scheme to blue"
    """
    from app.data.db.storage import Storage
    from app.server.config import Settings
    from app.modules.dashboard.services import DashboardService
    from app.modules.dashboard.models import RefineDashboardRequest

    settings = Settings()
    storage = Storage(settings)
    service = DashboardService(storage)

    req = RefineDashboardRequest(refinement=request)

    try:
        with console.status("[bold cyan]Refining dashboard...[/bold cyan]"):
            dashboard = asyncio.run(service.refine(dashboard_id, req))

        console.print(Panel(
            f"[bold green]✔ Dashboard refined successfully![/bold green]\n\n"
            f"[cyan]Name:[/cyan] {dashboard.name}\n"
            f"[cyan]Widgets:[/cyan] {len(dashboard.layout.widgets)}",
            title="Dashboard Refined",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]Error refining dashboard:[/red] {e}")
        raise click.Abort()

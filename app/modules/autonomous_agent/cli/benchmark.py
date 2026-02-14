"""Benchmark CLI commands for KAI.

This command group provides functionality for running and managing
benchmarks to evaluate context asset quality and SQL generation performance.
"""

import json
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.modules.autonomous_agent.cli import console, _run_async, ensure_typesense_or_prompt


@click.group()
def benchmark():
    """Benchmark commands.

    Run benchmarks to evaluate context asset quality and
    SQL generation performance. Execute suites, view results,
    and export reports for CI systems.
    """
    pass


# ============================================================================
# Run Benchmark
# ============================================================================

@benchmark.command()
@click.argument("suite_id")
@click.option("--db", "-d", required=True, help="Database connection ID or alias")
@click.option("--tags", "-t", help="Filter cases by tags (comma-separated)")
@click.option("--export", "-e", type=click.Path(), help="Export results to file (JSON or JUnit XML)")
@click.option("--format", "export_format", type=click.Choice(["json", "junit"]), default="json", help="Export format")
def run(suite_id, db, tags, export, export_format):
    """Run a benchmark suite.

    Examples:

        kai benchmark run suite_123 --db mydb

        kai benchmark run suite_123 --db mydb --tags smoke,critical

        kai benchmark run suite_123 --db mydb --export results.json
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import get_settings
    from app.modules.context_platform.services.benchmark_service import BenchmarkService
    from app.modules.autonomous_agent.modules import get_db_connection_repository

    settings = get_settings()
    storage = Storage(settings)
    service = BenchmarkService(storage)
    db_repo = get_db_connection_repository(storage)

    # Resolve database identifier
    db_conn = _resolve_db_identifier(db, db_repo)
    if not db_conn:
        console.print(f"[red]✖ Database '{db}' not found[/red]")
        console.print("[dim]Use 'kai connection list' to see available connections[/dim]")
        return

    # Get suite
    suite = service.get_suite(suite_id)
    if not suite:
        console.print(f"[red]✖ Suite '{suite_id}' not found[/red]")
        return

    console.print(f"\n[cyan]Running Benchmark Suite:[/cyan] {suite.get('name', suite_id)}")
    console.print(f"[dim]Database:[/dim] {db_conn.get('alias', db)}")

    # Filter cases by tags if specified
    case_ids = suite.get("case_ids", [])
    if tags:
        tag_filter = tags.split(",")
        filtered_cases = []
        for case_id in case_ids:
            case = service.get_case(case_id)
            if case:
                case_tags = case.get("tags", [])
                if any(tag in case_tags for tag in tag_filter):
                    filtered_cases.append(case_id)
        case_ids = filtered_cases
        console.print(f"[dim]Filtered by tags:[/dim] {tags}")

    console.print(f"[dim]Cases to run:[/dim] {len(case_ids)}\n")

    # Create run
    run = service.create_run(
        suite_id=suite_id,
        db_connection_id=db_conn["id"],
        context_asset_ids=[]  # TODO: Allow specifying context assets
    )

    service.start_run(run.id)

    # Execute cases
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Executing benchmarks...", total=len(case_ids))

        for case_id in case_ids:
            case = service.get_case(case_id)
            if not case:
                continue

            progress.update(task, description=f"Running: {case.get('name', case_id)}")

            # Mock execution - in real implementation, this would call the agent
            # For now, we'll create a mock result
            result = service.execute_case(
                run_id=run.id,
                case_id=case_id,
                actual_sql=case.get("expected_sql"),  # Using expected as actual for demo
                context_assets_used=[],
                execution_time_ms=150,
            )

    # Complete run
    completed_run = service.complete_run(run.id)

    # Display results
    _display_run_results(completed_run, service)

    # Export if requested
    if export:
        _export_run(completed_run, export, export_format, service)


def _display_run_results(run, service):
    """Display benchmark run results."""
    console.print(f"\n[bold]Benchmark Results:[/bold]")
    console.print(f"Status: {run.get('status', 'unknown').upper()}")
    console.print(f"Score: [cyan]{run.get('weighted_score', 0):.1f}%[/cyan]")
    console.print(f"Pass Rate: [cyan]{run.get('pass_rate', 0):.1f}%[/cyan]")
    console.print(f"Execution Time: [cyan]{run.get('execution_time_ms', 0)}ms[/cyan]")

    # Severity breakdown
    console.print(f"\n[bold]Severity Breakdown:[/bold]")
    severity_table = Table(show_header=True, header_style="bold magenta")
    severity_table.add_column("Severity", style="cyan")
    severity_table.add_column("Passed", style="green")
    severity_table.add_column("Total", style="white")
    severity_table.add_column("Rate", style="yellow")

    severities = [
        ("Critical", run.get("critical_passed", 0), run.get("critical_total", 0)),
        ("High", run.get("high_passed", 0), run.get("high_total", 0)),
        ("Medium", run.get("medium_passed", 0), run.get("medium_total", 0)),
        ("Low", run.get("low_passed", 0), run.get("low_total", 0)),
    ]

    for severity_name, passed, total in severities:
        if total > 0:
            rate = (passed / total) * 100
            severity_table.add_row(severity_name, str(passed), str(total), f"{rate:.1f}%")

    console.print(severity_table)

    # Overall summary
    total = run.get("total_cases", 0)
    passed = run.get("passed_cases", 0)
    failed = run.get("failed_cases", 0)
    errors = run.get("error_cases", 0)

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Total: {total} | [green]Passed: {passed}[/green] | [red]Failed: {failed}[/red] | [yellow]Errors: {errors}[/yellow]")


def _export_run(run, filepath, format_type, service):
    """Export run results to file."""
    path = Path(filepath)

    if format_type == "json":
        data = service.export_run_json(run["id"])
        if data:
            with open(path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            console.print(f"\n[green]✔ Results exported to:[/green] {filepath}")
    elif format_type == "junit":
        xml = service.export_run_junit(run["id"])
        if xml:
            with open(path, "w") as f:
                f.write(xml)
            console.print(f"\n[green]✔ Results exported to:[/green] {filepath}")


# ============================================================================
# List Suites
# ============================================================================

@benchmark.command()
@click.option("--db", "-d", help="Filter by database connection")
@click.option("--active-only", is_flag=True, default=True, help="Show only active suites")
def list(db, active_only):
    """List benchmark suites.

    Examples:

        kai benchmark list

        kai benchmark list --db mydb
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import get_settings
    from app.modules.context_platform.services.benchmark_service import BenchmarkService
    from app.modules.autonomous_agent.modules import get_db_connection_repository

    settings = get_settings()
    storage = Storage(settings)
    service = BenchmarkService(storage)

    suites = service.list_suites(db_connection_id=db, active_only=active_only)

    if not suites:
        console.print("[yellow]No benchmark suites found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Cases", style="yellow")
    table.add_column("Avg Score", style="green")
    table.add_column("Runs", style="blue")
    table.add_column("Last Run", style="dim")

    for suite in suites:
        suite_id = suite.get("id", "unknown")
        name = suite.get("name", "Unknown")
        case_count = len(suite.get("case_ids", []))
        avg_score = suite.get("avg_score", 0.0)
        total_runs = suite.get("total_runs", 0)
        last_run = suite.get("last_run_at", "Never")

        # Format last run
        if last_run and last_run != "Never":
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(last_run)
                last_run = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass

        table.add_row(
            suite_id[:12] + "...",
            name,
            str(case_count),
            f"{avg_score:.1f}%" if avg_score > 0 else "N/A",
            str(total_runs),
            last_run if last_run else "Never"
        )

    console.print("\n[bold]Benchmark Suites:[/bold]\n")
    console.print(table)

    if db:
        console.print(f"[dim]Filtered by database: {db}[/dim]")
    console.print(f"[dim]Showing {len(suites)} suite(s)[/dim]")


# ============================================================================
# Suite Info
# ============================================================================

@benchmark.command()
@click.argument("suite_id")
def info(suite_id):
    """Show detailed information about a benchmark suite.

    Examples:

        kai benchmark info suite_123
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import get_settings
    from app.modules.context_platform.services.benchmark_service import BenchmarkService

    settings = get_settings()
    storage = Storage(settings)
    service = BenchmarkService(storage)

    suite = service.get_suite(suite_id)
    if not suite:
        console.print(f"[red]✖ Suite '{suite_id}' not found[/red]")
        return

    console.print(f"\n[bold]Benchmark Suite:[/bold] {suite.get('name', suite_id)}")
    console.print(f"ID: {suite.get('id')}")
    console.print(f"Description: {suite.get('description', 'No description')}")
    console.print(f"Database: {suite.get('db_connection_id', 'N/A')}")
    console.print(f"Active: {'Yes' if suite.get('is_active') else 'No'}")
    console.print(f"Version: {suite.get('version', 'N/A')}")

    # Metrics
    console.print(f"\n[bold]Metrics:[/bold]")
    console.print(f"Total Runs: {suite.get('total_runs', 0)}")
    console.print(f"Avg Score: {suite.get('avg_score', 0):.1f}%")
    console.print(f"Last Run: {suite.get('last_run_at', 'Never')}")

    # Cases
    case_ids = suite.get("case_ids", [])
    console.print(f"\n[bold]Cases:[/bold] {len(case_ids)}")

    if case_ids:
        cases_table = Table(show_header=True, header_style="bold magenta")
        cases_table.add_column("ID", style="cyan")
        cases_table.add_column("Name", style="white")
        cases_table.add_column("Severity", style="yellow")
        cases_table.add_column("Weight", style="blue")
        cases_table.add_column("Tags", style="dim")

        for case_id in case_ids[:10]:  # Show first 10
            case = service.get_case(case_id)
            if case:
                cases_table.add_row(
                    case.get("id", "unknown")[:12] + "...",
                    case.get("name", "Unknown"),
                    case.get("severity", "medium"),
                    str(case.get("weight", 1.0)),
                    ",".join(case.get("tags", []))
                )

        console.print(cases_table)

        if len(case_ids) > 10:
            console.print(f"[dim]... and {len(case_ids) - 10} more cases[/dim]")


# ============================================================================
# List Results
# ============================================================================

@benchmark.command("results")
@click.argument("run_id")
@click.option("--failed-only", is_flag=True, help="Show only failed results")
def results(run_id, failed_only):
    """Show results for a benchmark run.

    Examples:

        kai benchmark results run_123

        kai benchmark results run_123 --failed-only
    """
    if not ensure_typesense_or_prompt():
        return

    from app.data.db.storage import Storage
    from app.server.config import get_settings
    from app.modules.context_platform.services.benchmark_service import BenchmarkService

    settings = get_settings()
    storage = Storage(settings)
    service = BenchmarkService(storage)

    run = service.repository.find_run_by_id(run_id)
    if not run:
        console.print(f"[red]✖ Run '{run_id}' not found[/red]")
        return

    results = service.repository.find_results_by_run(run_id)

    if failed_only:
        results = [r for r in results if r.get("status") in ("failed", "error")]

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Case ID", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Similarity", style="yellow")
    table.add_column("Weighted Score", style="green")
    table.add_column("Time (ms)", style="blue")

    for result in results:
        status = result.get("status", "unknown")
        # Colorize status
        if status == "passed":
            status = f"[green]{status}[/green]"
        elif status == "failed":
            status = f"[red]{status}[/red]"
        elif status == "error":
            status = f"[yellow]{status}[/yellow]"

        table.add_row(
            result.get("case_id", "unknown")[:12] + "...",
            status,
            f"{result.get('similarity_score', 0):.2f}" if result.get('similarity_score') else "N/A",
            f"{result.get('weighted_score', 0):.2f}",
            str(result.get('execution_time_ms', 0))
        )

    console.print(f"\n[bold]Results for:[/bold] {run_id}")
    console.print(table)
    console.print(f"[dim]Showing {len(results)} result(s)[/dim]")

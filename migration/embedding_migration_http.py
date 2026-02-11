#!/usr/bin/env python3
"""
HTTP-based embedding migration script.

Migrates embeddings by calling the existing API endpoints instead of direct database access:
- Instructions: Uses PUT endpoint (auto-regenerates embeddings)
- Context stores: Uses POST + DELETE (create new first, then delete old - safer approach)

Usage:
    python -m migration.embedding_migration_http
    python -m migration.embedding_migration_http --base-url http://localhost:8000
    python -m migration.embedding_migration_http --collections instructions
    python -m migration.embedding_migration_http --dry-run
    python -m migration.embedding_migration_http --backup-before  # Backup before migration
"""

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

import requests  # type: ignore
from tqdm import tqdm  # type: ignore
from urllib.parse import urljoin

# Import backup manager for pre-migration backup
from migration.backup_http import (
    BackupRestoreHTTP,
    generate_backup_path,
    DEFAULT_BACKUP_DIR,
)


@dataclass
class MigrationStats:
    """Track migration statistics."""
    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0


class EmbeddingMigrationHTTP:
    """HTTP-based embedding migration using API endpoints."""

    VALID_COLLECTIONS = {"instructions", "context_stores", "all"}

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        dry_run: bool = False,
        verbose: bool = True
    ):
        self.base_url = base_url.rstrip("/")
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats: dict[str, Any] = {}
        self.session = requests.Session()
        self.disable_pbar = not verbose

    def _log(self, message: str, force: bool = False) -> None:
        """Print log message if verbose or forced."""
        if self.verbose or force:
            print(message)

    def _get(self, path: str, params: dict | None = None) -> dict | list:
        """Make a GET request to the API."""
        url = urljoin(self.base_url, path)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, data: dict) -> dict:
        """Make a POST request to the API."""
        url = urljoin(self.base_url, path)
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def _put(self, path: str, data: dict) -> dict:
        """Make a PUT request to the API."""
        url = urljoin(self.base_url, path)
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

    def _delete(self, path: str) -> None:
        """Make a DELETE request to the API."""
        url = urljoin(self.base_url, path)
        response = self.session.delete(url)
        response.raise_for_status()

    def get_all_db_connections(self) -> list[dict]:
        """Get all database connections."""
        self._log("Fetching database connections...")
        result = self._get("/api/v1/database-connections")
        return cast(list[dict], result)

    def migrate_instructions(self, db_connection_id: str) -> MigrationStats:
        """Migrate instructions using PUT endpoint.

        The PUT endpoint auto-regenerates embeddings when condition/rules are updated.
        """
        stats = MigrationStats()

        try:
            instructions = cast(list[dict], self._get(
                "/api/v1/instructions",
                params={"db_connection_id": db_connection_id}
            ))

            # Filter out default instructions (no embeddings)
            non_default = [i for i in instructions if not i.get("is_default", False)]
            stats.total = len(non_default)

            if stats.total == 0:
                self._log("  No non-default instructions to migrate")
                return stats

            self._log(f"  Found {stats.total} non-default instructions")

            with tqdm(total=stats.total, desc="  Migrating instructions", disable=self.disable_pbar) as pbar:
                for instruction in non_default:
                    instr_id = instruction["id"]
                    condition = instruction.get("condition", "")
                    rules = instruction.get("rules", "")
                    is_default = instruction.get("is_default", False)
                    metadata = instruction.get("metadata")

                    # Skip default instructions (they don't have embeddings)
                    if is_default:
                        stats.skipped += 1
                        pbar.update(1)
                        continue

                    pbar.set_postfix_str(f"ID: {instr_id[:8]}...")

                    if self.dry_run:
                        stats.success += 1
                        pbar.update(1)
                        continue

                    try:
                        # PUT with same data - service auto-regenerates embedding
                        self._put(
                            f"/api/v1/instructions/{instr_id}",
                            data={
                                "condition": condition,
                                "rules": rules,
                                "is_default": is_default,
                                "metadata": metadata,
                            }
                        )
                        stats.success += 1
                        pbar.set_postfix_str(f"ID: {instr_id[:8]}... ✓")

                    except Exception:
                        stats.failed += 1
                        pbar.set_postfix_str(f"ID: {instr_id[:8]}... ✗")

                    pbar.update(1)

        except Exception as e:
            self._log(f"  Failed to fetch instructions: {e}", force=True)

        return stats

    def migrate_context_stores(self, db_connection_id: str) -> MigrationStats:
        """Migrate context stores using POST + DELETE (safer: creates new before deleting old)."""
        stats = MigrationStats()

        try:
            context_stores = cast(list[dict], self._get(
                "/api/v1/context-stores",
                params={"db_connection_id": db_connection_id}
            ))
            stats.total = len(context_stores)

            if stats.total == 0:
                self._log("  No context stores to migrate")
                return stats

            self._log(f"  Found {stats.total} context stores")

            with tqdm(total=stats.total, desc="  Migrating context stores", disable=self.disable_pbar) as pbar:
                for store in context_stores:
                    store_id = store["id"]
                    pbar.set_postfix_str(f"ID: {store_id[:8]}...")

                    # Store the data for recreation
                    store_data = {
                        "db_connection_id": db_connection_id,
                        "prompt_text": store.get("prompt_text", ""),
                        "sql": store.get("sql", ""),
                        "metadata": store.get("metadata"),
                    }

                    if self.dry_run:
                        stats.success += 1
                        pbar.update(1)
                        continue

                    try:
                        # POST first: Create new record with fresh embedding
                        new_store = self._post("/api/v1/context-stores", data=store_data)
                        new_id = new_store.get("id", "")

                        # Then DELETE the old record (safer: if delete fails, we have a duplicate)
                        self._delete(f"/api/v1/context-stores/{store_id}")
                        stats.success += 1
                        pbar.set_postfix_str(f"ID: {store_id[:8]}... ✓")

                    except Exception as e:
                        stats.failed += 1
                        pbar.set_postfix_str(f"ID: {store_id[:8]}... ✗")
                        self._log(f"    ERROR: {e}", force=True)

                    pbar.update(1)

        except Exception as e:
            self._log(f"  Failed to fetch context stores: {e}", force=True)

        return stats

    def run(self, collections: list[str]) -> dict[str, MigrationStats]:
        """Run the migration for specified collections."""
        results: dict[str, MigrationStats] = {}

        # Normalize collection names
        migrate_all = "all" in collections
        migrate_instructions = migrate_all or "instructions" in collections
        migrate_context_stores = migrate_all or "context_stores" in collections

        # Get all database connections
        db_connections = self.get_all_db_connections()

        if not db_connections:
            self._log("No database connections found", force=True)
            return results

        self._log(f"Found {len(db_connections)} database connection(s)")

        for db_conn in db_connections:
            db_id = db_conn["id"]
            db_name = db_conn.get("database_name", db_id)
            self._log(f"\n{'='*60}", force=True)
            self._log(f"Processing database: {db_name} ({db_id})", force=True)
            self._log(f"{'='*60}", force=True)

            if migrate_instructions:
                self._log("\n[Migrating Instructions]")
                stats = self.migrate_instructions(db_id)
                results[f"instructions:{db_id}"] = stats
                self._print_stats(stats, "Instructions")

            if migrate_context_stores:
                self._log("\n[Migrating Context Stores]")
                stats = self.migrate_context_stores(db_id)
                results[f"context_stores:{db_id}"] = stats
                self._print_stats(stats, "Context Stores")

        return results

    def _print_stats(self, stats: MigrationStats, label: str) -> None:
        """Print migration statistics."""
        self._log(f"\n  {label} Summary:")
        self._log(f"    Total:   {stats.total}")
        self._log(f"    Success: {stats.success}")
        self._log(f"    Failed:  {stats.failed}")
        self._log(f"    Skipped: {stats.skipped}")

    def print_final_summary(self, results: dict[str, MigrationStats]) -> None:
        """Print final summary of all migrations."""
        total_success = sum(s.success for s in results.values())
        total_failed = sum(s.failed for s in results.values())
        total_skipped = sum(s.skipped for s in results.values())

        self._log(f"\n{'='*60}", force=True)
        self._log("FINAL SUMMARY", force=True)
        self._log(f"{'='*60}", force=True)
        self._log(f"  Total Success: {total_success}", force=True)
        self._log(f"  Total Failed:  {total_failed}", force=True)
        self._log(f"  Total Skipped: {total_skipped}", force=True)
        self._log(f"{'='*60}", force=True)

        if total_failed > 0:
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HTTP-based embedding migration using API endpoints"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("MIGRATION_BASE_URL", "http://localhost:8000"),
        help="Base URL of the API service (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        choices=["all", "instructions", "context_stores"],
        default=["all"],
        help="Collections to migrate (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    parser.add_argument(
        "--backup-before",
        action="store_true",
        help="Create a backup before running migration"
    )
    parser.add_argument(
        "--backup-output",
        type=str,
        default="",
        help="Custom path for backup file (default: auto-generated in migration/backups/)"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("[DRY RUN MODE] No changes will be made\n")

    # Create backup if requested
    backup_file = None
    if args.backup_before and not args.dry_run:
        print("\n" + "=" * 60)
        print("Creating backup before migration...")
        print("=" * 60 + "\n")

        backup_manager = BackupRestoreHTTP(
            base_url=args.base_url,
            verbose=not args.quiet
        )

        output_path = args.backup_output
        if not output_path:
            output_path = generate_backup_path(DEFAULT_BACKUP_DIR)

        backup_data = backup_manager.create_backup()
        backup_file = backup_manager.save_backup(backup_data, output_path)

        print(f"\nBackup created successfully: {backup_file}")
        print("You can restore from this backup if migration fails.\n")

    migration = EmbeddingMigrationHTTP(
        base_url=args.base_url,
        dry_run=args.dry_run,
        verbose=not args.quiet
    )

    results = migration.run(args.collections)
    migration.print_final_summary(results)

    # Print backup info after migration completes
    if backup_file:
        print(f"\nBackup file: {backup_file}")
        print("To restore if needed: python -m migration.backup_http restore --input <backup-file>")


if __name__ == "__main__":
    main()

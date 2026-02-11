#!/usr/bin/env python3
"""
HTTP-based Backup Script for Instructions and Context Stores.

This script uses HTTP API endpoints to:
1. Backup all records by fetching from API endpoints
2. Restore records by posting to API endpoints

Usage:
    # Backup all records
    python -m migration.backup_http backup
    python -m migration.backup_http backup --base-url http://localhost:8000 --output backups/backup_2024-01-01.json

    # Restore from backup
    python -m migration.backup_http restore --input backups/backup_2024-01-01.json --base-url http://localhost:8000

    # List existing backups
    python -m migration.backup_http list

    # Dry run
    python -m migration.backup_http backup --dry-run
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import requests  # type: ignore
from tqdm import tqdm  # type: ignore
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


DEFAULT_BACKUP_DIR = "migration/backups"
DEFAULT_BASE_URL = "http://localhost:8000"


@dataclass
class BackupData:
    """Container for all backup data with metadata."""
    backup_date: str
    backup_version: str
    base_url: str
    instructions: list[dict]
    context_stores: list[dict]
    stats: dict[str, Any]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "backup_date": self.backup_date,
            "backup_version": self.backup_version,
            "base_url": self.base_url,
            "instructions": self.instructions,
            "context_stores": self.context_stores,
            "stats": self.stats,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackupData":
        """Create from dictionary."""
        return cls(
            backup_date=data["backup_date"],
            backup_version=data["backup_version"],
            base_url=data.get("base_url", ""),
            instructions=data.get("instructions", []),
            context_stores=data.get("context_stores", []),
            stats=data.get("stats", {}),
        )


class BackupRestoreHTTP:
    """HTTP-based backup and restore using API endpoints."""

    def __init__(
        self,
        base_url: str,
        verbose: bool = True
    ):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.session = requests.Session()
        self.disable_pbar = not verbose

    def _log(self, message: str, force: bool = False) -> None:
        """Print log message if verbose or forced."""
        if self.verbose or force:
            logger.info(message)

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

    def get_all_db_connections(self) -> list[dict]:
        """Get all database connections."""
        self._log("Fetching database connections...")
        try:
            result = self._get("/api/v1/database-connections")
            return list(result) if result else []
        except Exception as e:
            self._log(f"Failed to fetch database connections: {e}", force=True)
            return []

    def get_all_instructions(self) -> list[dict]:
        """Fetch all instructions from all database connections."""
        self._log("Fetching all instructions...")
        all_instructions = []

        db_connections = self.get_all_db_connections()

        for db_conn in db_connections:
            db_id = db_conn["id"]
            db_name = db_conn.get("database_name", db_id)
            self._log(f"  Fetching instructions for: {db_name} ({db_id})")

            try:
                instructions = list(self._get(
                    "/api/v1/instructions",
                    params={"db_connection_id": db_id}
                ))
                all_instructions.extend(instructions)
            except Exception as e:
                self._log(f"    Failed: {e}", force=True)

        return all_instructions

    def get_all_context_stores(self) -> list[dict]:
        """Fetch all context stores from all database connections."""
        self._log("Fetching all context stores...")
        all_context_stores = []

        db_connections = self.get_all_db_connections()

        for db_conn in db_connections:
            db_id = db_conn["id"]
            db_name = db_conn.get("database_name", db_id)
            self._log(f"  Fetching context stores for: {db_name} ({db_id})")

            try:
                stores = list(self._get(
                    "/api/v1/context-stores",
                    params={"db_connection_id": db_id}
                ))
                all_context_stores.extend(stores)
            except Exception as e:
                self._log(f"    Failed: {e}", force=True)

        return all_context_stores

    def _count_by_db_connection(self, records: list[dict], db_key: str = "db_connection_id") -> dict[str, int]:
        """Count records per database connection."""
        counts: dict[str, int] = {}
        for record in records:
            db_id = record.get(db_key, "unknown")
            counts[db_id] = counts.get(db_id, 0) + 1
        return counts

    def _count_defaults(self, records: list[dict]) -> dict[str, int]:
        """Count default vs non-default records."""
        defaults = sum(1 for r in records if r.get("is_default", False) is True)
        non_defaults = sum(1 for r in records if r.get("is_default", False) is False)
        return {"default": defaults, "non_default": non_defaults}

    def create_backup(self, dry_run: bool = False) -> BackupData:
        """Create a backup by fetching all records via HTTP API."""
        self._log("=" * 60, force=True)
        self._log("CREATING BACKUP (HTTP)", force=True)
        self._log("=" * 60, force=True)
        self._log(f"Base URL: {self.base_url}", force=True)

        if dry_run:
            self._log("[DRY RUN] No backup file will be created", force=True)

        # Fetch all records via HTTP
        instructions = self.get_all_instructions()
        context_stores = self.get_all_context_stores()

        # Calculate statistics
        instruction_counts = self._count_defaults(instructions)
        stats = {
            "instructions": {
                "total": len(instructions),
                "default": instruction_counts["default"],
                "non_default": instruction_counts["non_default"],
                "by_db_connection": self._count_by_db_connection(instructions),
            },
            "context_stores": {
                "total": len(context_stores),
                "by_db_connection": self._count_by_db_connection(context_stores),
            },
        }

        # Print summary
        self._log("", force=True)
        self._log("Backup Summary:", force=True)
        self._log(f"  Instructions: {len(instructions)} total", force=True)
        self._log(f"    - Default: {instruction_counts['default']}", force=True)
        self._log(f"    - Non-default: {instruction_counts['non_default']}", force=True)
        self._log(f"  Context Stores: {len(context_stores)} total", force=True)
        self._log("", force=True)

        backup_data = BackupData(
            backup_date=datetime.now().isoformat(),
            backup_version="1.0",
            base_url=self.base_url,
            instructions=instructions,
            context_stores=context_stores,
            stats=stats,
        )

        return backup_data

    def save_backup(self, backup_data: BackupData, output_path: str) -> str:
        """Save backup data to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(backup_data.to_dict(), f, indent=2)

        self._log(f"Backup saved to: {output_file}", force=True)
        return str(output_file)

    def load_backup(self, input_path: str) -> BackupData:
        """Load backup data from a JSON file."""
        with open(input_path, "r") as f:
            data = json.load(f)

        return BackupData.from_dict(data)

    def restore_backup(self, backup_data: BackupData, dry_run: bool = False) -> dict[str, dict[str, int]]:
        """Restore records from a backup via HTTP API.

        Returns statistics about the restore operation.
        """
        self._log("=" * 60, force=True)
        self._log("RESTORING FROM BACKUP (HTTP)", force=True)
        self._log(f"Backup Date: {backup_data.backup_date}", force=True)
        self._log(f"Backup Version: {backup_data.backup_version}", force=True)
        self._log(f"Base URL: {self.base_url}", force=True)
        self._log("=" * 60, force=True)

        if dry_run:
            self._log("[DRY RUN] No records will be restored", force=True)

        stats = {
            "instructions": {"created": 0, "skipped": 0, "failed": 0},
            "context_stores": {"created": 0, "skipped": 0, "failed": 0},
        }

        # Restore instructions
        self._log("", force=True)
        self._log(f"Restoring {len(backup_data.instructions)} instructions...", force=True)

        with tqdm(total=len(backup_data.instructions), desc="  Instructions", disable=self.disable_pbar) as pbar:
            for record in backup_data.instructions:
                record_id = record.get("id", "")
                is_default = record.get("is_default", False)
                db_connection_id = record.get("db_connection_id", "")

                pbar.set_postfix_str(f"ID: {record_id[:8] if record_id else 'unknown'}...")

                if dry_run:
                    stats["instructions"]["created"] += 1
                    pbar.update(1)
                    continue

                try:
                    # POST to create new instruction (without id - let server generate)
                    data_for_post = {
                        "db_connection_id": db_connection_id,
                        "condition": record.get("condition", ""),
                        "rules": record.get("rules", ""),
                        "is_default": is_default,
                        "metadata": record.get("metadata"),
                    }

                    new_record = self._post("/api/v1/instructions", data=data_for_post)
                    stats["instructions"]["created"] += 1
                    pbar.set_postfix_str(f"ID: {record_id[:8] if record_id else 'unknown'}... ✓")

                except Exception as e:
                    stats["instructions"]["failed"] += 1
                    pbar.set_postfix_str(f"ID: {record_id[:8] if record_id else 'unknown'}... ✗")
                    self._log(f"    ERROR: {e}", force=True)

                pbar.update(1)

        # Restore context stores
        self._log("", force=True)
        self._log(f"Restoring {len(backup_data.context_stores)} context stores...", force=True)

        with tqdm(total=len(backup_data.context_stores), desc="  Context Stores", disable=self.disable_pbar) as pbar:
            for record in backup_data.context_stores:
                record_id = record.get("id", "")
                db_connection_id = record.get("db_connection_id", "")

                pbar.set_postfix_str(f"ID: {record_id[:8] if record_id else 'unknown'}...")

                if dry_run:
                    stats["context_stores"]["created"] += 1
                    pbar.update(1)
                    continue

                try:
                    # POST to create new context store (without id - let server generate)
                    data_for_post = {
                        "db_connection_id": db_connection_id,
                        "prompt_text": record.get("prompt_text", ""),
                        "sql": record.get("sql", ""),
                        "metadata": record.get("metadata"),
                    }

                    new_record = self._post("/api/v1/context-stores", data=data_for_post)
                    stats["context_stores"]["created"] += 1
                    pbar.set_postfix_str(f"ID: {record_id[:8] if record_id else 'unknown'}... ✓")

                except Exception as e:
                    stats["context_stores"]["failed"] += 1
                    pbar.set_postfix_str(f"ID: {record_id[:8] if record_id else 'unknown'}... ✗")
                    self._log(f"    ERROR: {e}", force=True)

                pbar.update(1)

        # Print summary
        self._log("", force=True)
        self._log("Restore Summary:", force=True)
        self._log(f"  Instructions: {stats['instructions']['created']} created, "
                  f"{stats['instructions']['skipped']} skipped, "
                  f"{stats['instructions']['failed']} failed", force=True)
        self._log(f"  Context Stores: {stats['context_stores']['created']} created, "
                  f"{stats['context_stores']['skipped']} skipped, "
                  f"{stats['context_stores']['failed']} failed", force=True)
        self._log("", force=True)

        return stats

    def list_backups(self, backup_dir: str = DEFAULT_BACKUP_DIR) -> list[dict]:
        """List all backup files in the backup directory."""
        backup_path = Path(backup_dir)

        if not backup_path.exists():
            self._log(f"Backup directory does not exist: {backup_dir}")
            return []

        backups = []
        for file in backup_path.glob("backup_*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)

                backups.append({
                    "file": str(file),
                    "date": data.get("backup_date", "unknown"),
                    "version": data.get("backup_version", "unknown"),
                    "base_url": data.get("base_url", "unknown"),
                    "instructions": data.get("stats", {}).get("instructions", {}).get("total", 0),
                    "context_stores": data.get("stats", {}).get("context_stores", {}).get("total", 0),
                })
            except Exception as e:
                self._log(f"Error reading backup file {file}: {e}")

        # Sort by date (newest first)
        backups.sort(key=lambda x: x["date"], reverse=True)

        return backups


def generate_backup_path(backup_dir: str = DEFAULT_BACKUP_DIR) -> str:
    """Generate a unique backup file path with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(backup_dir, f"backup_{timestamp}.json")


def main():
    parser = argparse.ArgumentParser(
        description="HTTP-based backup and restore for instructions and context stores",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "action",
        choices=["backup", "restore", "list"],
        help="Action to perform"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("MIGRATION_BASE_URL", DEFAULT_BASE_URL),
        help=f"Base URL of the API (default: from env or {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="",
        help="Output path for backup file (default: auto-generated)"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input path for restore file"
    )
    parser.add_argument(
        "--backup-dir",
        type=str,
        default=DEFAULT_BACKUP_DIR,
        help=f"Backup directory (default: {DEFAULT_BACKUP_DIR})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )

    args = parser.parse_args()

    manager = BackupRestoreHTTP(
        base_url=args.base_url,
        verbose=not args.quiet
    )

    if args.action == "backup":
        # Generate output path if not specified
        output_path = args.output
        if not output_path:
            output_path = generate_backup_path(args.backup_dir)

        backup_data = manager.create_backup(dry_run=args.dry_run)

        if not args.dry_run:
            manager.save_backup(backup_data, output_path)

    elif args.action == "restore":
        if not args.input:
            print("Error: --input is required for restore operation")
            sys.exit(1)

        backup_data = manager.load_backup(args.input)
        stats = manager.restore_backup(backup_data, dry_run=args.dry_run)

        # Exit with error if any failures
        total_failed = (
            stats["instructions"]["failed"] +
            stats["context_stores"]["failed"]
        )
        if total_failed > 0:
            sys.exit(1)

    elif args.action == "list":
        backups = manager.list_backups(args.backup_dir)

        print(f"\nBackups in {args.backup_dir}:")
        print("=" * 80)

        if not backups:
            print("No backups found")
        else:
            for backup in backups:
                print(f"\nFile: {backup['file']}")
                print(f"  Date: {backup['date']}")
                print(f"  Version: {backup['version']}")
                print(f"  Base URL: {backup['base_url']}")
                print(f"  Instructions: {backup['instructions']}")
                print(f"  Context Stores: {backup['context_stores']}")

        print("=" * 80)


if __name__ == "__main__":
    main()

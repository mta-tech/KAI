#!/usr/bin/env python3
"""
Backup and Restore Script for Instructions and Context Stores.

This script provides functionality to:
1. Backup all records (instructions and context-stores) to a JSON file
2. Restore records from a backup JSON file

Usage:
    # Backup all records (uses environment variables)
    python -m migration.backup_restore backup
    python -m migration.backup_restore backup --output backups/backup_2024-01-01.json

    # Backup with explicit Typesense credentials
    python -m migration.backup_restore backup --typesense-url http://localhost:8108 --typesense-api-key xyz

    # Restore from backup
    python -m migration.backup_restore restore --input backups/backup_2024-01-01.json

    # List existing backups
    python -m migration.backup_restore list

    # Dry run (preview what would be backed up)
    python -m migration.backup_restore backup --dry-run
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

import typesense  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


DEFAULT_BACKUP_DIR = "migration/backups"
DEFAULT_TYPESENSE_URL = "http://localhost:8108"
DEFAULT_TYPESENSE_API_KEY = "Hu52dwsas2Adxd2"


@dataclass
class BackupRecord:
    """Represents a single record in the backup."""
    id: str
    data: dict
    is_default: bool | None = None


@dataclass
class BackupData:
    """Container for all backup data with metadata."""
    backup_date: str
    backup_version: str
    instructions: list[BackupRecord]
    context_stores: list[BackupRecord]
    stats: dict[str, Any]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "backup_date": self.backup_date,
            "backup_version": self.backup_version,
            "instructions": [asdict(r) for r in self.instructions],
            "context_stores": [asdict(r) for r in self.context_stores],
            "stats": self.stats,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackupData":
        """Create from dictionary."""
        return cls(
            backup_date=data["backup_date"],
            backup_version=data["backup_version"],
            instructions=[BackupRecord(**r) for r in data.get("instructions", [])],
            context_stores=[BackupRecord(**r) for r in data.get("context_stores", [])],
            stats=data.get("stats", {}),
        )


class BackupRestoreManager:
    """Manages backup and restore operations for instructions and context stores."""

    COLLECTIONS = ["instructions", "context_stores"]

    def __init__(
        self,
        typesense_url: str,
        typesense_api_key: str,
        verbose: bool = True
    ):
        self.typesense_url = typesense_url
        self.typesense_api_key = typesense_api_key
        self.verbose = verbose
        self.client = self._create_client()

    def _log(self, message: str, force: bool = False) -> None:
        """Print log message if verbose or forced."""
        if self.verbose or force:
            logger.info(message)

    def _create_client(self) -> typesense.Client:
        """Create and return a Typesense client."""
        return typesense.Client({
            'api_key': self.typesense_api_key,
            'nodes': [{
                'host': self._extract_host(self.typesense_url),
                'port': self._extract_port(self.typesense_url),
                'protocol': self._extract_protocol(self.typesense_url),
            }],
            'connection_timeout_seconds': 2,
        })

    def _extract_host(self, url: str) -> str:
        """Extract host from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.hostname or "localhost"

    def _extract_port(self, url: str) -> int:
        """Extract port from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.port or (443 if parsed.scheme == "https" else 80)

    def _extract_protocol(self, url: str) -> str:
        """Extract protocol from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.scheme or "http"

    def _ensure_collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        try:
            self.client.collections[collection_name].retrieve()
            return True
        except Exception:
            return False

    def _get_all_documents(self, collection_name: str) -> list[dict]:
        """Fetch all documents from a collection with pagination."""
        if not self._ensure_collection_exists(collection_name):
            self._log(f"Collection '{collection_name}' does not exist, skipping...")
            return []

        all_docs = []
        page = 1
        per_page = 250

        while True:
            search_params = {
                "q": "*",
                "per_page": per_page,
                "page": page,
            }

            results = self.client.collections[collection_name].documents.search(search_params)

            if results["found"] == 0:
                break

            docs = [hit["document"] for hit in results["hits"]]
            all_docs.extend(docs)

            if len(docs) < per_page:
                break

            page += 1

        return all_docs

    def _count_by_db_connection(self, records: list[dict], db_key: str = "db_connection_id") -> dict[str, int]:
        """Count records per database connection."""
        counts: dict[str, int] = {}
        for record in records:
            db_id = record.get(db_key, "unknown")
            counts[db_id] = counts.get(db_id, 0) + 1
        return counts

    def create_backup(self, dry_run: bool = False) -> BackupData:
        """Create a backup of all instructions and context stores."""
        self._log("=" * 60, force=True)
        self._log("CREATING BACKUP", force=True)
        self._log("=" * 60, force=True)
        self._log(f"Typesense URL: {self.typesense_url}", force=True)

        if dry_run:
            self._log("[DRY RUN] No backup file will be created", force=True)

        # Fetch all records
        instructions = self._get_all_documents("instructions")
        context_stores = self._get_all_documents("context_stores")

        # Create backup records
        instruction_backups = []
        for doc in instructions:
            record = BackupRecord(
                id=doc.get("id", ""),
                data=doc,
                is_default=doc.get("is_default", False)
            )
            instruction_backups.append(record)

        context_store_backups = []
        for doc in context_stores:
            record = BackupRecord(
                id=doc.get("id", ""),
                data=doc,
                is_default=None  # Context stores don't have is_default flag
            )
            context_store_backups.append(record)

        # Calculate statistics
        instruction_defaults = sum(1 for r in instruction_backups if r.is_default is True)
        instruction_non_defaults = sum(1 for r in instruction_backups if r.is_default is False)

        stats = {
            "instructions": {
                "total": len(instruction_backups),
                "default": instruction_defaults,
                "non_default": instruction_non_defaults,
                "by_db_connection": self._count_by_db_connection(instructions),
            },
            "context_stores": {
                "total": len(context_store_backups),
                "by_db_connection": self._count_by_db_connection(context_stores),
            },
        }

        # Print summary
        self._log("", force=True)
        self._log("Backup Summary:", force=True)
        self._log(f"  Instructions: {len(instruction_backups)} total", force=True)
        self._log(f"    - Default: {instruction_defaults}", force=True)
        self._log(f"    - Non-default: {instruction_non_defaults}", force=True)
        self._log(f"  Context Stores: {len(context_store_backups)} total", force=True)
        self._log("", force=True)

        backup_data = BackupData(
            backup_date=datetime.now().isoformat(),
            backup_version="1.0",
            instructions=instruction_backups,
            context_stores=context_store_backups,
            stats=stats,
        )

        return backup_data

    def save_backup(self, backup_data: BackupData, output_path: str) -> str:
        """Save backup data to a JSON file."""
        # Ensure directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(output_file, "w") as f:
            json.dump(backup_data.to_dict(), f, indent=2)

        self._log(f"Backup saved to: {output_file}", force=True)
        return str(output_file)

    def load_backup(self, input_path: str) -> BackupData:
        """Load backup data from a JSON file."""
        with open(input_path, "r") as f:
            data = json.load(f)

        return BackupData.from_dict(data)

    def _find_one(self, collection_name: str, filter_dict: dict) -> dict | None:
        """Find a single document by filter."""
        if not self._ensure_collection_exists(collection_name):
            return None

        filter_parts = [f"{k}:={v}" for k, v in filter_dict.items()]
        filter_string = " && ".join(filter_parts)

        search_params = {
            "q": "*",
            "filter_by": filter_string,
            "per_page": 1,
        }

        results = self.client.collections[collection_name].documents.search(search_params)

        if results["found"] > 0:
            return results["hits"][0]["document"]
        return None

    def _insert_one(self, collection_name: str, doc: dict) -> str:
        """Insert a document into a collection."""
        import uuid
        doc = doc.copy()
        doc["id"] = doc.get("id", str(uuid.uuid4()))
        result = self.client.collections[collection_name].documents.create(doc)
        return result.get("id", doc["id"])

    def restore_backup(self, backup_data: BackupData, dry_run: bool = False) -> dict[str, dict[str, int]]:
        """Restore records from a backup.

        Returns statistics about the restore operation.
        """
        self._log("=" * 60, force=True)
        self._log("RESTORING FROM BACKUP", force=True)
        self._log(f"Backup Date: {backup_data.backup_date}", force=True)
        self._log(f"Backup Version: {backup_data.backup_version}", force=True)
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

        for record in backup_data.instructions:
            record_id = record.data.get("id")
            is_default = record.data.get("is_default", False)

            # Check if record already exists
            existing = self._find_one("instructions", {"id": record_id})

            if existing:
                self._log(f"  SKIP: Instruction {record_id[:8] if record_id else 'unknown'}... already exists (is_default={is_default})")
                stats["instructions"]["skipped"] += 1
                continue

            if dry_run:
                stats["instructions"]["created"] += 1
                continue

            try:
                # Remove id from data so storage generates a new one
                data_for_insert = {k: v for k, v in record.data.items() if k != "id"}
                new_id = self._insert_one("instructions", data_for_insert)
                stats["instructions"]["created"] += 1
                self._log(f"  OK: Instruction {record_id[:8] if record_id else 'unknown'}... restored as {new_id[:8]}... (is_default={is_default})")
            except Exception as e:
                stats["instructions"]["failed"] += 1
                self._log(f"  FAIL: Instruction {record_id[:8] if record_id else 'unknown'}... - {e}", force=True)

        # Restore context stores
        self._log("", force=True)
        self._log(f"Restoring {len(backup_data.context_stores)} context stores...", force=True)

        for record in backup_data.context_stores:
            record_id = record.data.get("id")

            # Check if record already exists
            existing = self._find_one("context_stores", {"id": record_id})

            if existing:
                self._log(f"  SKIP: Context Store {record_id[:8] if record_id else 'unknown'}... already exists")
                stats["context_stores"]["skipped"] += 1
                continue

            if dry_run:
                stats["context_stores"]["created"] += 1
                continue

            try:
                # Remove id from data so storage generates a new one
                data_for_insert = {k: v for k, v in record.data.items() if k != "id"}
                new_id = self._insert_one("context_stores", data_for_insert)
                stats["context_stores"]["created"] += 1
                self._log(f"  OK: Context Store {record_id[:8] if record_id else 'unknown'}... restored as {new_id[:8]}...")
            except Exception as e:
                stats["context_stores"]["failed"] += 1
                self._log(f"  FAIL: Context Store {record_id[:8] if record_id else 'unknown'}... - {e}", force=True)

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


def get_typesense_config_from_env() -> tuple[str, str]:
    """Get Typesense configuration from environment variables."""
    url = os.getenv("TYPESENSE_URL", os.getenv("TYPESENSE_HOST", DEFAULT_TYPESENSE_URL))
    api_key = os.getenv("TYPESENSE_API_KEY", DEFAULT_TYPESENSE_API_KEY)
    return url, api_key


def main():
    parser = argparse.ArgumentParser(
        description="Backup and restore instructions and context stores",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "action",
        choices=["backup", "restore", "list"],
        help="Action to perform"
    )
    parser.add_argument(
        "--typesense-url",
        type=str,
        default=os.getenv("TYPESENSE_URL", os.getenv("TYPESENSE_HOST", DEFAULT_TYPESENSE_URL)),
        help=f"Typesense URL (default: from env or {DEFAULT_TYPESENSE_URL})"
    )
    parser.add_argument(
        "--typesense-api-key",
        type=str,
        default=os.getenv("TYPESENSE_API_KEY", DEFAULT_TYPESENSE_API_KEY),
        help=f"Typesense API key (default: from env or default)"
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

    manager = BackupRestoreManager(
        typesense_url=args.typesense_url,
        typesense_api_key=args.typesense_api_key,
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
                print(f"  Instructions: {backup['instructions']}")
                print(f"  Context Stores: {backup['context_stores']}")

        print("=" * 80)


if __name__ == "__main__":
    main()

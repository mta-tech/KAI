"""
Embedding Migration Script

This script re-embeds all records when the embedding model configuration changes.
Run this after updating .env with new embedding model settings.

Usage:
    poetry run python -m migration.embedding_migration
    # Or with specific collections:
    poetry run python -m migration/embedding_migration.py --collections instructions context_stores
    # Or dry run:
    poetry run python -m migration/embedding_migration.py --dry-run
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, ".")

from app.server.config import Settings
from app.data.db.storage import Storage
from app.utils.model.embedding_model import EmbeddingModel

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Collections with their embedding configurations
COLLECTIONS_CONFIG = {
    "context_stores": {
        "embedding_field": "prompt_embedding",
        "text_field": "prompt_text",
        "exclude_fields": ["prompt_embedding"],
    },
    "instructions": {
        "embedding_field": "instruction_embedding",
        "text_fields": ["condition", "rules"],
        "filter": "is_default:=false",  # Only re-embed non-default instructions
        "exclude_fields": ["instruction_embedding"],
    },
    "table_descriptions": {
        "embedding_field": "table_embedding",
        # Table embeddings are computed dynamically from table_representation
        # This is more complex - skip for now or implement separately
        "skip": True,
    },
}


class EmbeddingMigration:
    """Migrates embeddings to a new model configuration."""

    def __init__(self, dry_run: bool = False):
        self.settings = Settings()
        self.storage = Storage(self.settings)
        self.embedding_model = EmbeddingModel().get_model()
        self.dry_run = dry_run

        # Get current embedding config
        self.config = {
            "family": self.settings.EMBEDDING_FAMILY,
            "model": self.settings.EMBEDDING_MODEL,
            "dimensions": self.settings.EMBEDDING_DIMENSIONS,
        }

    def _get_all_documents(self, collection: str, filter_by: str = None) -> list[dict]:
        """Fetch all documents from a collection."""
        all_docs = []
        page = 1
        per_page = 250

        while True:
            search_params = {
                "q": "*",
                "per_page": per_page,
                "page": page,
            }

            if filter_by:
                search_params["filter_by"] = filter_by

            results = self.storage.client.collections[collection].documents.search(
                search_params
            )

            if results["found"] == 0:
                break

            docs = [hit["document"] for hit in results["hits"]]
            all_docs.extend(docs)

            if len(docs) < per_page:
                break

            page += 1

        return all_docs

    def _compute_embedding(self, doc: dict, config: dict) -> list[float] | None:
        """Compute embedding for a document based on its configuration."""
        text_fields = config.get("text_fields", [])
        text_field = config.get("text_field")

        if text_fields:
            # Combine multiple text fields
            text_parts = [str(doc.get(field, "")) for field in text_fields]
            text = ", ".join(text_parts)
        elif text_field:
            text = str(doc.get(text_field, ""))
        else:
            return None

        try:
            return self.embedding_model.embed_query(text)
        except Exception as e:
            logger.error(f"Failed to compute embedding for document {doc.get('id')}: {e}")
            return None

    def _update_document(
        self, collection: str, doc_id: str, embedding: list[float], embedding_field: str
    ) -> bool:
        """Update a document with new embedding."""
        try:
            self.storage.client.collections[collection].documents[doc_id].update(
                {embedding_field: embedding}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False

    def migrate_collection(self, collection_name: str) -> dict:
        """Migrate all documents in a collection."""
        config = COLLECTIONS_CONFIG.get(collection_name, {})

        if config.get("skip"):
            logger.info(f"Skipping {collection_name} (marked for skip)")
            return {"status": "skipped", "count": 0}

        embedding_field = config["embedding_field"]
        filter_by = config.get("filter")
        exclude_fields = config.get("exclude_fields", [])

        logger.info(f"Starting migration for '{collection_name}'...")
        logger.info(f"  - Embedding field: {embedding_field}")
        logger.info(f"  - Filter: {filter_by or 'none'}")
        logger.info(f"  - Current config: {self.config}")

        # Get all documents
        docs = self._get_all_documents(collection_name, filter_by)
        total_count = len(docs)

        if total_count == 0:
            logger.info(f"  No documents found in '{collection_name}'")
            return {"status": "success", "count": 0}

        logger.info(f"  Found {total_count} documents to migrate")

        if self.dry_run:
            logger.info(f"  [DRY RUN] Would migrate {total_count} documents")
            return {"status": "dry_run", "count": total_count}

        # Migrate each document
        success_count = 0
        failed_count = 0

        with tqdm(total=total_count, desc=f"  Migrating {collection_name}") as pbar:
            for doc in docs:
                doc_id = doc.get("id")
                if not doc_id:
                    failed_count += 1
                    pbar.update(1)
                    continue

                # Compute new embedding
                embedding = self._compute_embedding(doc, config)

                if embedding is None:
                    failed_count += 1
                    pbar.update(1)
                    continue

                # Update document
                if self._update_document(collection_name, doc_id, embedding, embedding_field):
                    success_count += 1
                else:
                    failed_count += 1

                pbar.update(1)

        logger.info(f"  Migration complete: {success_count} succeeded, {failed_count} failed")

        return {
            "status": "completed",
            "count": total_count,
            "success": success_count,
            "failed": failed_count,
        }

    def migrate(self, collections: list[str] = None) -> dict:
        """Run migration for specified collections or all collections."""
        if collections is None:
            collections = [
                name for name, config in COLLECTIONS_CONFIG.items()
                if not config.get("skip")
            ]

        logger.info("=" * 60)
        logger.info("EMBEDDING MIGRATION")
        logger.info("=" * 60)
        logger.info(f"New embedding config: {self.config}")
        logger.info(f"Collections to migrate: {collections}")
        if self.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        logger.info("=" * 60)

        results = {}
        for collection in collections:
            results[collection] = self.migrate_collection(collection)

        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)

        for collection, result in results.items():
            logger.info(f"{collection}: {result}")

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Migrate embeddings to a new model configuration"
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        choices=["context_stores", "instructions", "table_descriptions", "all"],
        default=["all"],
        help="Collections to migrate (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making any changes",
    )

    args = parser.parse_args()

    # Resolve collections
    if "all" in args.collections:
        collections = None  # Will migrate all non-skipped collections
    else:
        collections = args.collections

    # Run migration
    migration = EmbeddingMigration(dry_run=args.dry_run)
    results = migration.migrate(collections)

    # Exit with error if any migration failed
    for result in results.values():
        if result.get("status") == "completed" and result.get("failed", 0) > 0:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

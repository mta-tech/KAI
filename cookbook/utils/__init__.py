"""
KAI Cookbook - Shared Utilities

Common utility functions for all cookbook scripts.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests

# Default API configuration
DEFAULT_BASE_URL = "http://localhost:8015"
API_PREFIX = "/api/v1"

# Load sample database URI from environment
# This is the Kementerian Koperasi database hosted on Neon
SAMPLE_DB_URI = os.getenv(
    "SAMPLE_DB_URI",
    "postgresql://neondb_owner:npg_6Lua4kAFJnhg@ep-blue-bar-a1ptyhib-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
SAMPLE_DB_ALIAS = "kemenkop_sample"


def parse_cookbook_args() -> argparse.Namespace:
    """
    Parse common command-line arguments for cookbook scripts.

    Returns:
        argparse.Namespace: Parsed arguments with 'cleanup' boolean flag
    """
    parser = argparse.ArgumentParser(
        description="KAI Cookbook - Run with optional cleanup",
        add_help=True
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Preserve created resources (skip cleanup at the end)"
    )
    return parser.parse_args()


class KAIAPIClient:
    """Simple HTTP client for KAI API."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _make_url(self, path: str) -> str:
        """Construct full URL from path."""
        return f"{self.base_url}{API_PREFIX}{path}"

    def get(self, path: str, params: dict | None = None) -> dict:
        """Make GET request."""
        response = self.session.get(self._make_url(path), params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, data: dict | None = None, json_data: dict | None = None, params: dict | None = None) -> dict:
        """Make POST request."""
        response = self.session.post(
            self._make_url(path),
            data=data,
            json=json_data,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def put(self, path: str, json_data: dict | None = None) -> dict:
        """Make PUT request."""
        response = self.session.put(self._make_url(path), json=json_data)
        response.raise_for_status()
        return response.json()

    def delete(self, path: str) -> dict:
        """Make DELETE request."""
        response = self.session.delete(self._make_url(path))
        response.raise_for_status()
        return response.json()


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print("\n" + "-" * 40)
    print(f"  {title}")
    print("-" * 40)


def print_response(response: dict | list, title: str = "Response") -> None:
    """Pretty print API response."""
    print_subsection(title)
    print(json.dumps(response, indent=2, ensure_ascii=False))


def press_to_continue(message: str = "Press Enter to continue...") -> None:
    """Pause and wait for user input."""
    input(f"\n{message}")


def find_by_name(items: list[dict], name: str, name_key: str = "name") -> dict | None:
    """Find an item in a list by name."""
    for item in items:
        if item.get(name_key) == name:
            return item
    return None


def find_by_id(items: list[dict], item_id: str, id_key: str = "id") -> dict | None:
    """Find an item in a list by ID."""
    for item in items:
        if item.get(id_key) == item_id:
            return item
    return None


def get_or_create(
    items: list[dict],
    name: str,
    create_func: callable,
    name_key: str = "name"
) -> dict:
    """Get existing item by name or create a new one."""
    existing = find_by_name(items, name, name_key)
    if existing:
        print(f"  ✓ Found existing: {name}")
        return existing

    print(f"  → Creating new: {name}")
    return create_func()


def sanitize_name(name: str) -> str:
    """Sanitize a name for use as identifier."""
    return name.lower().replace(" ", "_").replace("-", "_")[:50]


class IdempotentCreator:
    """Helper class for idempotent resource creation."""

    def __init__(self, client: KAIAPIClient):
        self.client = client
        self._cache: dict[str, Any] = {}

    def get_or_create_connection(
        self,
        alias: str,
        connection_uri: str,
        schemas: list[str] | None = None
    ) -> dict:
        """Get existing connection or create new one."""
        if alias in self._cache:
            return self._cache[alias]

        connections = self.client.get("/database-connections")
        existing = find_by_name(connections, alias, "alias")

        if existing:
            print(f"  ✓ Using existing connection: {alias}")
            self._cache[alias] = existing
            return existing

        print(f"  → Creating new connection: {alias}")
        connection = self.client.post("/database-connections", json_data={
            "alias": alias,
            "connection_uri": connection_uri,
            "schemas": schemas,
            "metadata": {"created_by": "cookbook"}
        })
        self._cache[alias] = connection
        return connection

    def cleanup_connection(self, connection_id: str) -> None:
        """Delete a connection by ID."""
        try:
            self.client.delete(f"/database-connections/{connection_id}")
            print(f"  ✓ Deleted connection: {connection_id}")
        except requests.HTTPError as e:
            print(f"  ! Failed to delete connection: {e}")

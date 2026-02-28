"""Mission artifact models with provenance tracking.

Artifacts are outputs produced during mission execution that can be
linked to mission runs and traced back to their source context assets.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ArtifactType(str, Enum):
    """Type of mission artifact."""

    VERIFIED_SQL = "verified_sql"
    NOTEBOOK = "notebook"
    SUMMARY = "summary"
    CHART = "chart"
    INSIGHT = "insight"


@dataclass
class ArtifactProvenance:
    """Provenance information linking artifact to source assets.

    Tracks the lineage of artifacts to enable traceability and
    attribution of context assets used in generation.
    """

    # Source context assets that contributed to this artifact
    source_asset_ids: list[str] = field(default_factory=list)
    source_asset_types: list[str] = field(default_factory=list)

    # Mission that produced this artifact
    mission_id: str = ""
    mission_stage: str | None = None

    # Generation metadata
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    generation_method: str | None = None  # e.g., "llm", "template", "hybrid"

    # Attribution
    generated_by: str | None = None  # Agent or service that created it
    confidence: float = 0.0  # Confidence in artifact quality (0-1)


@dataclass
class MissionArtifact:
    """Base artifact produced during mission execution.

    All artifacts include provenance information for traceability
    to source context assets and mission context.
    """

    id: str
    artifact_type: ArtifactType
    mission_id: str
    name: str
    description: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Content varies by artifact_type
    content: dict[str, Any] = field(default_factory=dict)

    # Provenance tracking
    provenance: ArtifactProvenance = field(default_factory=ArtifactProvenance)

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerifiedSQLArtifact(MissionArtifact):
    """Artifact for verified SQL query candidates.

    Represents SQL queries that have been validated and can be
    reused in future missions or promoted to context assets.
    """

    artifact_type: ArtifactType = field(default=ArtifactType.VERIFIED_SQL, init=False)

    # SQL-specific content
    sql_query: str = ""
    query_hash: str | None = field(default=None, init=False)  # Auto-generated from sql_query
    execution_count: int = 0
    avg_execution_time_ms: int = 0

    # Validation metadata
    is_validated: bool = False
    validation_errors: list[str] = field(default_factory=list)
    row_count_estimate: int | None = None

    # Reuse tracking
    reuse_count: int = 0
    promoted_to_asset_id: str | None = None  # If promoted to context asset

    def __post_init__(self):
        """Auto-generate query hash from SQL query."""
        if self.sql_query and not self.query_hash:
            import hashlib
            self.query_hash = hashlib.md5(self.sql_query.encode()).hexdigest()[:16]


@dataclass
class NotebookArtifact(MissionArtifact):
    """Artifact for notebook generation.

    Notebooks are structured workflows that can be reused for
    similar analysis tasks.
    """

    artifact_type: ArtifactType = field(default=ArtifactType.NOTEBOOK, init=False)

    # Notebook-specific content
    notebook_id: str | None = None  # If persisted to notebook service
    cell_count: int = 0
    parameter_count: int = 0

    # Analysis metadata
    analysis_type: str | None = None  # e.g., "timeseries", "comparison"
    database_alias: str | None = None

    # Reuse tracking
    reuse_count: int = 0
    promoted_to_asset_id: str | None = None


@dataclass
class SummaryArtifact(MissionArtifact):
    """Artifact for mission summary with provenance.

    Summarizes the mission results, key findings, and links
    to all other artifacts produced.
    """

    artifact_type: ArtifactType = field(default=ArtifactType.SUMMARY, init=False)

    # Summary content
    question: str = ""
    answer: str = ""
    key_findings: list[str] = field(default_factory=list)
    methodology: str | None = None

    # Linked artifacts
    linked_artifact_ids: list[str] = field(default_factory=list)
    sql_queries_used: list[str] = field(default_factory=list)

    # Quality metrics
    confidence_score: float = 0.0
    completeness_score: float = 0.0  # How completely the question was answered

    # Follow-up suggestions
    suggested_questions: list[str] = field(default_factory=list)

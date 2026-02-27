# tests/modules/autonomous_agent/test_artifact_models.py
"""
Tests for Mission Artifact Models

These tests verify the Pydantic/dataclass models for mission artifacts, including:
- MissionArtifact model validation
- VerifiedSQLArtifact model validation
- NotebookArtifact model validation
- SummaryArtifact model validation
- ArtifactProvenance tracking
- ArtifactType enum validation

Prerequisites:
- Mission artifact models implemented in app/modules/autonomous_agent/models/artifact.py

Task: #77 (Add Mission Artifacts)
Status: READY - Models implemented, adding tests
"""

import pytest
from datetime import datetime
from app.modules.autonomous_agent.models.artifact import (
    ArtifactProvenance,
    ArtifactType,
    MissionArtifact,
    VerifiedSQLArtifact,
    NotebookArtifact,
    SummaryArtifact,
)


# ============================================================================
# ArtifactProvenance Model Tests
# ============================================================================

class TestArtifactProvenance:
    """Tests for ArtifactProvenance model."""

    def test_should_create_provenance_with_required_fields(self):
        """Should create ArtifactProvenance with required fields."""
        provenance = ArtifactProvenance(
            mission_id="mission_123",
        )
        assert provenance.mission_id == "mission_123"
        assert provenance.source_asset_ids == []
        assert provenance.source_asset_types == []

    def test_should_track_source_asset_ids(self):
        """Should track source asset IDs for provenance."""
        provenance = ArtifactProvenance(
            mission_id="mission_123",
            source_asset_ids=["asset_1", "asset_2"],
        )
        assert len(provenance.source_asset_ids) == 2
        assert "asset_1" in provenance.source_asset_ids

    def test_should_set_generated_at_automatically(self):
        """Should set generated_at timestamp automatically."""
        provenance = ArtifactProvenance(mission_id="mission_123")
        assert provenance.generated_at is not None
        # Should be ISO format string
        assert isinstance(provenance.generated_at, str)

    def test_should_store_generation_metadata(self):
        """Should store generation method and agent."""
        provenance = ArtifactProvenance(
            mission_id="mission_123",
            generation_method="llm",
            generated_by="sql_agent",
            confidence=0.85,
        )
        assert provenance.generation_method == "llm"
        assert provenance.generated_by == "sql_agent"
        assert provenance.confidence == 0.85

    def test_should_track_mission_stage(self):
        """Should track the mission stage that produced the artifact."""
        provenance = ArtifactProvenance(
            mission_id="mission_123",
            mission_stage="execute",
        )
        assert provenance.mission_stage == "execute"


# ============================================================================
# MissionArtifact Model Tests
# ============================================================================

class TestMissionArtifact:
    """Tests for MissionArtifact model."""

    def test_should_create_artifact_with_required_fields(self):
        """Should create MissionArtifact with required fields."""
        artifact = MissionArtifact(
            id="artifact_123",
            artifact_type=ArtifactType.SUMMARY,
            mission_id="mission_123",
            name="Test Artifact",
        )
        assert artifact.id == "artifact_123"
        assert artifact.artifact_type == ArtifactType.SUMMARY
        assert artifact.mission_id == "mission_123"
        assert artifact.name == "Test Artifact"

    def test_should_set_created_at_automatically(self):
        """Should set created_at timestamp automatically."""
        artifact = MissionArtifact(
            id="artifact_123",
            artifact_type=ArtifactType.SUMMARY,
            mission_id="mission_123",
            name="Test Artifact",
        )
        assert artifact.created_at is not None
        assert isinstance(artifact.created_at, str)

    def test_should_store_content_dict(self):
        """Should store content as dictionary."""
        artifact = MissionArtifact(
            id="artifact_123",
            artifact_type=ArtifactType.SUMMARY,
            mission_id="mission_123",
            name="Test Artifact",
            content={"key": "value"},
        )
        assert artifact.content == {"key": "value"}

    def test_should_include_provenance(self):
        """Should include provenance information."""
        provenance = ArtifactProvenance(mission_id="mission_123")
        artifact = MissionArtifact(
            id="artifact_123",
            artifact_type=ArtifactType.SUMMARY,
            mission_id="mission_123",
            name="Test Artifact",
            provenance=provenance,
        )
        assert artifact.provenance.mission_id == "mission_123"

    def test_should_support_tags(self):
        """Should support tags for categorization."""
        artifact = MissionArtifact(
            id="artifact_123",
            artifact_type=ArtifactType.SUMMARY,
            mission_id="mission_123",
            name="Test Artifact",
            tags=["summary", "analysis"],
        )
        assert "summary" in artifact.tags
        assert "analysis" in artifact.tags


# ============================================================================
# VerifiedSQLArtifact Model Tests
# ============================================================================

class TestVerifiedSQLArtifact:
    """Tests for VerifiedSQLArtifact model."""

    def test_should_create_sql_artifact_with_query(self):
        """Should create VerifiedSQLArtifact with SQL query."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM sales",
        )
        assert artifact.artifact_type == ArtifactType.VERIFIED_SQL
        assert artifact.sql_query == "SELECT * FROM sales"

    def test_should_generate_query_hash(self):
        """Should generate query hash for deduplication."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM sales",
        )
        assert artifact.query_hash is not None
        assert len(artifact.query_hash) == 16  # MD5 hash truncated

    def test_should_track_validation_status(self):
        """Should track whether query is validated."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM sales",
            is_validated=True,
        )
        assert artifact.is_validated is True

    def test_should_store_validation_errors(self):
        """Should store validation errors."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM",
            is_validated=False,
            validation_errors=["syntax error near end of input"],
        )
        assert len(artifact.validation_errors) == 1
        assert "syntax error" in artifact.validation_errors[0]

    def test_should_track_execution_metrics(self):
        """Should track execution count and time."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM sales",
            execution_count=5,
            avg_execution_time_ms=150,
        )
        assert artifact.execution_count == 5
        assert artifact.avg_execution_time_ms == 150

    def test_should_track_reuse_count(self):
        """Should track how many times query has been reused."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM sales",
            reuse_count=3,
        )
        assert artifact.reuse_count == 3

    def test_should_link_to_promoted_asset(self):
        """Should link to context asset if promoted."""
        artifact = VerifiedSQLArtifact(
            id="sql_123",
            mission_id="mission_123",
            name="Sales Query",
            sql_query="SELECT * FROM sales",
            promoted_to_asset_id="asset_456",
        )
        assert artifact.promoted_to_asset_id == "asset_456"


# ============================================================================
# NotebookArtifact Model Tests
# ============================================================================

class TestNotebookArtifact:
    """Tests for NotebookArtifact model."""

    def test_should_create_notebook_artifact(self):
        """Should create NotebookArtifact with notebook details."""
        artifact = NotebookArtifact(
            id="nb_123",
            mission_id="mission_123",
            name="Sales Analysis Notebook",
            notebook_id="notebook_456",
            cell_count=5,
            parameter_count=2,
        )
        assert artifact.artifact_type == ArtifactType.NOTEBOOK
        assert artifact.notebook_id == "notebook_456"
        assert artifact.cell_count == 5
        assert artifact.parameter_count == 2

    def test_should_track_analysis_type(self):
        """Should track analysis type."""
        artifact = NotebookArtifact(
            id="nb_123",
            mission_id="mission_123",
            name="Sales Analysis Notebook",
            analysis_type="timeseries",
        )
        assert artifact.analysis_type == "timeseries"

    def test_should_track_database_alias(self):
        """Should track database alias."""
        artifact = NotebookArtifact(
            id="nb_123",
            mission_id="mission_123",
            name="Sales Analysis Notebook",
            database_alias="sales_db",
        )
        assert artifact.database_alias == "sales_db"

    def test_should_track_reuse_and_promotion(self):
        """Should track reuse count and promotion to asset."""
        artifact = NotebookArtifact(
            id="nb_123",
            mission_id="mission_123",
            name="Sales Analysis Notebook",
            reuse_count=2,
            promoted_to_asset_id="skill_789",
        )
        assert artifact.reuse_count == 2
        assert artifact.promoted_to_asset_id == "skill_789"


# ============================================================================
# SummaryArtifact Model Tests
# ============================================================================

class TestSummaryArtifact:
    """Tests for SummaryArtifact model."""

    def test_should_create_summary_artifact(self):
        """Should create SummaryArtifact with question and answer."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
        )
        assert artifact.artifact_type == ArtifactType.SUMMARY
        assert artifact.question == "What are the total sales?"
        assert artifact.answer == "Total sales are $1M."

    def test_should_store_key_findings(self):
        """Should store key findings from analysis."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
            key_findings=["Sales increased 20%", "Top product: Widget A"],
        )
        assert len(artifact.key_findings) == 2
        assert "Sales increased 20%" in artifact.key_findings

    def test_should_track_methodology(self):
        """Should track analysis methodology."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
            methodology="Aggregated sales data from last quarter",
        )
        assert artifact.methodology == "Aggregated sales data from last quarter"

    def test_should_link_to_other_artifacts(self):
        """Should link to other artifacts produced in mission."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
            linked_artifact_ids=["sql_123", "chart_456"],
        )
        assert "sql_123" in artifact.linked_artifact_ids
        assert "chart_456" in artifact.linked_artifact_ids

    def test_should_track_sql_queries_used(self):
        """Should track SQL queries used in analysis."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
            sql_queries_used=["SELECT sum(amount) FROM sales"],
        )
        assert len(artifact.sql_queries_used) == 1

    def test_should_store_suggested_questions(self):
        """Should store suggested follow-up questions."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
            suggested_questions=["What about last month?", "Break down by region?"],
        )
        assert len(artifact.suggested_questions) == 2

    def test_should_track_quality_scores(self):
        """Should track confidence and completeness scores."""
        artifact = SummaryArtifact(
            id="summary_123",
            mission_id="mission_123",
            name="Mission Summary",
            question="What are the total sales?",
            answer="Total sales are $1M.",
            confidence_score=0.9,
            completeness_score=0.8,
        )
        assert artifact.confidence_score == 0.9
        assert artifact.completeness_score == 0.8


# ============================================================================
# ArtifactType Enum Tests
# ============================================================================

class TestArtifactType:
    """Tests for ArtifactType enum."""

    def test_should_have_all_expected_types(self):
        """Should have all expected artifact types."""
        assert ArtifactType.VERIFIED_SQL.value == "verified_sql"
        assert ArtifactType.NOTEBOOK.value == "notebook"
        assert ArtifactType.SUMMARY.value == "summary"
        assert ArtifactType.CHART.value == "chart"
        assert ArtifactType.INSIGHT.value == "insight"

    def test_should_be_string_enum(self):
        """Should be a string enum."""
        artifact_type = ArtifactType.VERIFIED_SQL
        assert isinstance(artifact_type.value, str)
        assert str(artifact_type) == "verified_sql"

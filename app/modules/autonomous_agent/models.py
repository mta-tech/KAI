from dataclasses import dataclass, field
from typing import Literal, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum

# Import artifact types conditionally to avoid circular imports
if TYPE_CHECKING:
    from app.modules.autonomous_agent.models.artifact import (
        ArtifactProvenance,
        ArtifactType,
        MissionArtifact,
        NotebookArtifact,
        SummaryArtifact,
        VerifiedSQLArtifact,
    )


class MissionStage(str, Enum):
    """Mission execution stages for proactive flow."""

    PLAN = "plan"
    EXPLORE = "explore"
    EXECUTE = "execute"
    SYNTHESIZE = "synthesize"
    FINALIZE = "finalize"
    FAILED = "failed"


class MissionState(str, Enum):
    """Overall mission state."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class AgentTask:
    """Task submitted to the autonomous agent."""
    id: str
    prompt: str
    db_connection_id: str
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    context: dict | None = None
    metadata: dict | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MissionPlan:
    """Mission plan for inspection and persistence.

    Stores the planned steps and decision points for a proactive mission.
    """

    mission_id: str
    stages: list[dict]  # Planned stages with their configurations
    estimated_steps: int
    estimated_duration_seconds: int
    confidence_estimate: float  # Overall confidence in this plan (0-1)
    reasoning: str  # Explanation of the plan
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Budget constraints for safety
    max_runtime_seconds: int = 180
    max_tool_calls: int = 40
    max_sql_retries: int = 3
    max_identical_failures: int = 2


@dataclass
class MissionStageDetail:
    """A single mission stage with state and confidence."""

    stage_type: MissionStage
    mission_id: str
    stage_id: str
    confidence: float  # Stage-level confidence (0-1)
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)
    output_summary: str | None = None
    artifacts_produced: list[str] = field(default_factory=list)  # IDs of artifacts


@dataclass
class MissionRun:
    """Mission-level state and confidence metadata.

    Tracks the overall execution of a proactive mission with
    confidence scoring and state transitions.
    """

    id: str
    session_id: str
    task_id: str
    question: str
    db_connection_id: str
    state: MissionState = MissionState.PENDING
    current_stage: MissionStage | None = None
    overall_confidence: float = 0.0  # Overall mission confidence (0-1)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: str | None = None
    completed_at: str | None = None

    # Mission metadata
    mode: Literal["analysis", "query", "script", "full_autonomy"] = "full_autonomy"
    total_steps: int = 0
    completed_steps: int = 0
    artifacts_produced: list[str] = field(default_factory=list)  # Artifact IDs

    # Mission plan reference
    mission_plan_id: str | None = None

    # Error information
    error: str | None = None
    failure_stage: MissionStage | None = None


@dataclass
class MissionStreamEvent:
    """Mission stream event for proactive flow.

    Emitted during mission execution to communicate stage transitions,
    confidence updates, and intermediate results.
    """

    version: str = "v1"
    type: Literal["mission_stage", "mission_update", "mission_error", "mission_complete"] = "mission_update"
    stage: MissionStage | None = None
    mission_id: str = ""
    session_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    payload: dict = field(default_factory=dict)

    # Event metadata
    sequence_number: int = 0
    confidence: float | None = None  # Confidence at this point in the mission
    stage_status: Literal["pending", "running", "completed", "failed", "skipped"] | None = None

    # For mission_stage events
    stage_id: str | None = None
    output_summary: str | None = None
    artifacts_produced: list[str] = field(default_factory=list)

    # For mission_error events
    error: str | None = None
    retry_count: int = 0
    can_retry: bool = False

    # For mission_complete events
    final_status: Literal["completed", "failed", "partial"] | None = None
    execution_time_ms: int = 0


@dataclass
class ChartSpec:
    """Specification for generated chart."""
    chart_type: Literal["line", "bar", "pie", "scatter", "area", "heatmap"]
    title: str
    x_column: str
    y_column: str | list[str]
    data: list[dict]
    color_column: str | None = None
    config: dict = field(default_factory=dict)  # Additional chart config


@dataclass
class Insight:
    """AI-generated insight from data."""
    category: Literal["trend", "anomaly", "comparison", "summary", "recommendation"]
    title: str
    description: str
    importance: Literal["high", "medium", "low"]
    supporting_data: dict | None = None


@dataclass
class SuggestedQuestion:
    """Follow-up question suggestion."""
    question: str
    category: Literal["drill_down", "compare", "trend", "filter", "aggregate"]
    rationale: str  # Why this question is relevant


@dataclass
class AgentResult:
    """Result from autonomous agent execution."""
    task_id: str
    mission_id: str  # New: Mission run ID for traceability
    status: Literal["completed", "failed", "partial"]
    final_answer: str
    # Mission-level metadata
    overall_confidence: float = 0.0  # Overall mission confidence (0-1)
    stages_completed: list[str] = field(default_factory=list)  # Completed stage IDs
    final_stage: MissionStage | None = None  # The stage where mission ended
    # GenBI outputs
    charts: list[ChartSpec] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    suggested_questions: list[SuggestedQuestion] = field(default_factory=list)
    # Execution details
    sql_queries: list[str] = field(default_factory=list)
    artifacts: list[dict] = field(
        default_factory=list,
        metadata={
            "description": "Mission artifacts with provenance. "
            "Use link_artifact_to_mission() to format. "
            "Each artifact contains: artifact_id, artifact_type, name, "
            "description, created_at, provenance"
        },
    )
    execution_time_ms: int = 0
    error: str | None = None

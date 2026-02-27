"""Feedback models for context platform.

Feedback allows users to report issues, suggest improvements, and validate
context assets and benchmark results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal, Any


class FeedbackType(str, Enum):
    """Type of feedback."""

    IMPROVEMENT = "improvement"
    BUG_REPORT = "bug_report"
    VALIDATION = "validation"
    SUGGESTION = "suggestion"
    OTHER = "other"


class FeedbackTargetType(str, Enum):
    """Type of entity the feedback is about."""

    CONTEXT_ASSET = "context_asset"
    BENCHMARK_CASE = "benchmark_case"
    BENCHMARK_RUN = "benchmark_run"
    MISSION_RUN = "mission_run"
    OTHER = "other"


class FeedbackStatus(str, Enum):
    """Status of feedback."""

    PENDING = "pending"
    REVIEWED = "reviewed"
    ADDRESSED = "addressed"
    DISMISSED = "dismissed"


@dataclass
class Feedback:
    """User feedback on context platform entities.

    Links feedback to specific entities for tracking and improvement.
    """

    id: str | None = None  # Typesense document ID
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # User information
    user_id: str | None = None  # User who submitted feedback
    user_email: str | None = None  # User email (optional)

    # Feedback classification
    feedback_type: FeedbackType = FeedbackType.OTHER
    target_type: FeedbackTargetType = FeedbackTargetType.OTHER

    # Target entity linkage
    target_id: str | None = None  # ID of the entity this feedback is about
    target_version: str | None = None  # Version of the target (if applicable)

    # Feedback content
    title: str = field(default="")  # Brief summary
    description: str = field(default="")  # Detailed feedback
    severity: Literal["low", "medium", "high", "critical"] = "medium"

    # Validation-specific fields
    validation_result: bool | None = None  # True=positive, False=negative
    validation_notes: str | None = None  # Additional validation context

    # Metadata
    status: FeedbackStatus = FeedbackStatus.PENDING
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Review information
    reviewed_by: str | None = None  # User who reviewed this feedback
    reviewed_at: str | None = None
    review_notes: str | None = None

    class Config:
        use_enum_values = True


@dataclass
class FeedbackRequest:
    """Request model for submitting feedback."""

    feedback_type: FeedbackType
    target_type: FeedbackTargetType
    target_id: str | None = None
    title: str = ""
    description: str = ""
    severity: Literal["low", "medium", "high", "critical"] = "medium"

    # Optional validation fields
    validation_result: bool | None = None
    validation_notes: str | None = None

    # Optional metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackResponse:
    """Response model for feedback."""

    id: str
    feedback_type: str
    target_type: str
    target_id: str | None
    title: str
    description: str
    severity: str
    status: str
    created_at: str
    updated_at: str

    # Validation fields
    validation_result: bool | None = None
    validation_notes: str | None = None

    # Review fields
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    review_notes: str | None = None

    # Metadata
    tags: list[str] = field(default_factory=list)

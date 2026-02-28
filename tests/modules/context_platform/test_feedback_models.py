# tests/modules/context_platform/test_feedback_models.py
"""Tests for Feedback models."""
import pytest
from app.modules.context_platform.models.feedback import (
    Feedback,
    FeedbackType,
    FeedbackTargetType,
    FeedbackStatus,
    FeedbackRequest,
)


class TestFeedback:
    """Tests for Feedback model."""

    def test_create_feedback(self):
        """Should create feedback with required fields."""
        feedback = Feedback(
            feedback_type=FeedbackType.IMPROVEMENT,
            target_type=FeedbackTargetType.CONTEXT_ASSET,
            title="Add more examples",
            description="This asset needs more examples",
        )
        assert feedback.feedback_type == FeedbackType.IMPROVEMENT
        assert feedback.target_type == FeedbackTargetType.CONTEXT_ASSET
        assert feedback.status == FeedbackStatus.PENDING


class TestFeedbackRequest:
    """Tests for FeedbackRequest model."""

    def test_create_feedback_request(self):
        """Should create feedback request."""
        request = FeedbackRequest(
            feedback_type=FeedbackType.BUG_REPORT,
            target_type=FeedbackTargetType.MISSION_RUN,
            target_id="mission_123",
            title="SQL Error",
            description="Query failed with syntax error",
        )
        assert request.feedback_type == FeedbackType.BUG_REPORT
        assert request.target_id == "mission_123"

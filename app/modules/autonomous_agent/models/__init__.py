"""Autonomous agent models."""

from app.modules.autonomous_agent.models.artifact import (
    ArtifactProvenance,
    ArtifactType,
    MissionArtifact,
    NotebookArtifact,
    SummaryArtifact,
    VerifiedSQLArtifact,
)

# Import core mission models from models.py (sibling file, not this package)
# Use importlib to bypass the package and import from the file directly
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "mission_models",
    str(Path(__file__).parent.parent / "models.py")
)
if _spec is None or _spec.loader is None:
    raise ImportError("Could not load mission models spec")
_mission_models = importlib.util.module_from_spec(_spec)
sys.modules["app.modules.autonomous_agent.mission_models"] = _mission_models
_spec.loader.exec_module(_mission_models)

# Re-export mission models
MissionStage = _mission_models.MissionStage
MissionState = _mission_models.MissionState
AgentTask = _mission_models.AgentTask
MissionPlan = _mission_models.MissionPlan
MissionStageDetail = _mission_models.MissionStageDetail
MissionRun = _mission_models.MissionRun
MissionStreamEvent = _mission_models.MissionStreamEvent
ChartSpec = _mission_models.ChartSpec
Insight = _mission_models.Insight
SuggestedQuestion = _mission_models.SuggestedQuestion
AgentResult = _mission_models.AgentResult

__all__ = [
    # Artifacts
    "ArtifactType",
    "ArtifactProvenance",
    "MissionArtifact",
    "VerifiedSQLArtifact",
    "NotebookArtifact",
    "SummaryArtifact",
    # Mission models
    "MissionStage",
    "MissionState",
    "AgentTask",
    "MissionPlan",
    "MissionStageDetail",
    "MissionRun",
    "MissionStreamEvent",
    "ChartSpec",
    "Insight",
    "SuggestedQuestion",
    "AgentResult",
]

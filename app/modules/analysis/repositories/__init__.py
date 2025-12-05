"""Repository for analysis results."""

from app.modules.analysis.models import AnalysisResult

DB_COLLECTION = "analysis_results"


class AnalysisRepository:
    """Repository for managing AnalysisResult documents in TypeSense."""

    def __init__(self, storage):
        self.storage = storage

    def insert(self, analysis: AnalysisResult) -> AnalysisResult:
        """Insert a new analysis result."""
        analysis_dict = analysis.model_dump(exclude={"id"})
        # Convert nested models to dicts for TypeSense
        analysis_dict["insights"] = [
            insight.model_dump() if hasattr(insight, "model_dump") else insight
            for insight in analysis_dict.get("insights", [])
        ]
        analysis_dict["chart_recommendations"] = [
            rec.model_dump() if hasattr(rec, "model_dump") else rec
            for rec in analysis_dict.get("chart_recommendations", [])
        ]
        if analysis_dict.get("llm_config"):
            analysis_dict["llm_config"] = (
                analysis_dict["llm_config"].model_dump()
                if hasattr(analysis_dict["llm_config"], "model_dump")
                else analysis_dict["llm_config"]
            )
        analysis.id = str(self.storage.insert_one(DB_COLLECTION, analysis_dict))
        return analysis

    def find_by_id(self, id: str) -> AnalysisResult | None:
        """Find an analysis result by ID."""
        row = self.storage.find_one(DB_COLLECTION, {"id": id})
        if not row:
            return None
        return AnalysisResult(**row)

    def find_by_sql_generation_id(self, sql_generation_id: str) -> list[AnalysisResult]:
        """Find all analysis results for a SQL generation."""
        rows = self.storage.find(DB_COLLECTION, {"sql_generation_id": sql_generation_id})
        return [AnalysisResult(**row) for row in rows]

    def update(self, analysis: AnalysisResult) -> AnalysisResult:
        """Update an existing analysis result."""
        analysis_dict = analysis.model_dump(exclude={"id"})
        # Convert nested models to dicts for TypeSense
        analysis_dict["insights"] = [
            insight.model_dump() if hasattr(insight, "model_dump") else insight
            for insight in analysis_dict.get("insights", [])
        ]
        analysis_dict["chart_recommendations"] = [
            rec.model_dump() if hasattr(rec, "model_dump") else rec
            for rec in analysis_dict.get("chart_recommendations", [])
        ]
        if analysis_dict.get("llm_config"):
            analysis_dict["llm_config"] = (
                analysis_dict["llm_config"].model_dump()
                if hasattr(analysis_dict["llm_config"], "model_dump")
                else analysis_dict["llm_config"]
            )
        self.storage.update_or_create(
            DB_COLLECTION,
            {"id": analysis.id},
            analysis_dict,
        )
        return analysis

    def delete_by_id(self, id: str) -> AnalysisResult | None:
        """Delete an analysis result by ID."""
        doc = self.storage.delete_by_id(DB_COLLECTION, id)
        return AnalysisResult(**doc) if doc else None


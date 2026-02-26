"""Skill tools for autonomous agent."""

import json
import logging

from app.data.db.storage import Storage
from app.modules.database_connection.models import DatabaseConnection
from app.modules.skill.services import SkillService

logger = logging.getLogger(__name__)


def create_list_skills_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to list all available skills."""
    service = SkillService(storage)

    def list_skills() -> str:
        """List all available skills for the current database connection.

        Returns a list of skills with their IDs, names, and descriptions.
        Use this to see what skills are available before loading one.

        Returns:
            JSON string with skill metadata for all active skills.
        """
        try:
            skills = service.get_active_skills(db_connection.id)

            if not skills:
                return json.dumps({
                    "success": True,
                    "message": "No skills available for this database connection.",
                    "skills": [],
                    "hint": "Skills can be added by placing SKILL.md files in the .skills/ directory and running discovery.",
                })

            skill_list = [
                {
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "description": s.description,
                    "category": s.category,
                    "tags": s.tags,
                }
                for s in skills
            ]

            return json.dumps({
                "success": True,
                "total": len(skill_list),
                "skills": skill_list,
                "hint": "Use load_skill(skill_id) to load full instructions for a skill.",
            }, indent=2)

        except Exception as e:
            logger.error(f"Error listing skills: {e}")
            return json.dumps({"success": False, "error": str(e)})

    return list_skills


def create_load_skill_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to load a skill's full content."""
    service = SkillService(storage)

    def load_skill(skill_id: str) -> str:
        """Load a skill's full instructions by its skill_id.

        Call this when you need the detailed instructions for a specific skill.
        Use list_skills() first to see available skills.

        Args:
            skill_id: The skill identifier (e.g., "analysis/revenue", "data-quality")

        Returns:
            The skill's full markdown content with instructions, or an error message.
        """
        try:
            skill = service.get_skill_by_skill_id(db_connection.id, skill_id)

            result = {
                "success": True,
                "skill_id": skill.skill_id,
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
                "tags": skill.tags,
                "content": skill.content,
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error loading skill '{skill_id}': {e}")
            return json.dumps({
                "success": False,
                "skill_id": skill_id,
                "error": str(e),
                "hint": "Use list_skills() to see available skills.",
            })

    return load_skill


def create_search_skills_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to search for relevant skills."""
    service = SkillService(storage)

    def search_skills(query: str, limit: int = 5) -> str:
        """Search for skills relevant to a query or topic.

        Uses semantic search to find skills that match the query.
        This is useful when you're not sure which skill to use.

        Args:
            query: Search query describing what you're trying to do
            limit: Maximum number of results (default: 5)

        Returns:
            JSON string with matching skills sorted by relevance.
        """
        try:
            skills = service.find_relevant_skills(
                db_connection.id, query, limit=limit
            )

            if not skills:
                return json.dumps({
                    "success": True,
                    "message": f"No skills found matching '{query}'",
                    "skills": [],
                    "hint": "Try a different search term or use list_skills() to see all available skills.",
                })

            skill_list = [
                {
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "description": s.description,
                    "category": s.category,
                    "relevance_hint": "Use load_skill(skill_id) to load full instructions",
                }
                for s in skills
            ]

            return json.dumps({
                "success": True,
                "query": query,
                "total": len(skill_list),
                "skills": skill_list,
            }, indent=2)

        except Exception as e:
            logger.error(f"Error searching skills: {e}")
            return json.dumps({"success": False, "error": str(e)})

    return search_skills


def create_find_skills_for_question_tool(
    db_connection: DatabaseConnection, storage: Storage
):
    """Create tool to automatically find skills relevant to a user's question."""
    service = SkillService(storage)

    def find_skills_for_question(question: str) -> str:
        """Automatically find skills that might help answer a user's question.

        This analyzes the question and returns any skills that could provide
        guidance on how to approach the analysis or answer.

        CALL THIS for complex analysis questions to check if there are
        predefined approaches or guidelines you should follow.

        Args:
            question: The user's question or analysis request

        Returns:
            JSON with relevant skills and their descriptions.
        """
        try:
            skills = service.find_relevant_skills(
                db_connection.id, question, limit=3
            )

            if not skills:
                return json.dumps({
                    "success": True,
                    "message": "No specific skills found for this question.",
                    "skills": [],
                    "recommendation": "Proceed with standard analysis approach.",
                })

            # Format skills with actionable recommendations
            skill_recommendations = []
            for skill in skills:
                skill_recommendations.append({
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "description": skill.description,
                    "recommendation": f"Consider loading skill '{skill.skill_id}' for guidance on: {skill.description}",
                })

            return json.dumps({
                "success": True,
                "question": question[:200] + "..." if len(question) > 200 else question,
                "relevant_skills": skill_recommendations,
                "action": "Load these skills to get specific instructions before proceeding with analysis.",
            }, indent=2)

        except Exception as e:
            logger.error(f"Error finding skills for question: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "recommendation": "Proceed with standard analysis approach.",
            })

    return find_skills_for_question

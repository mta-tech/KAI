"""Instruction tools for autonomous agent."""
import json

from app.modules.database_connection.models import DatabaseConnection
from app.data.db.storage import Storage


def create_get_instructions_tool(db_connection: DatabaseConnection, storage: Storage):
    """Create tool to get all instructions for the database connection."""
    from app.modules.instruction.repositories import InstructionRepository

    instruction_repo = InstructionRepository(storage)

    def get_instructions() -> str:
        """Get all custom instructions for the current database connection.

        Instructions are rules and guidelines that customize how you should
        respond to certain types of questions or handle specific data.

        Returns:
            JSON string with all instructions including:
            - condition: When this instruction applies
            - rules: What rules to follow
            - is_default: Whether this always applies
        """
        try:
            instructions = instruction_repo.find_by({"db_connection_id": db_connection.id})

            if not instructions:
                return json.dumps({
                    "success": True,
                    "message": "No custom instructions found for this database.",
                    "instructions": []
                })

            result = {
                "success": True,
                "instructions": [
                    {
                        "id": i.id,
                        "condition": i.condition,
                        "rules": i.rules,
                        "is_default": i.is_default,
                    }
                    for i in instructions
                ],
                "summary": {
                    "total": len(instructions),
                    "default_count": sum(1 for i in instructions if i.is_default),
                    "conditional_count": sum(1 for i in instructions if not i.is_default),
                }
            }

            return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return get_instructions


def get_instructions_for_prompt(db_connection_id: str, prompt_text: str, storage: Storage) -> str:
    """Get relevant instructions for a given prompt.

    This function retrieves both default instructions and semantically
    relevant instructions based on the prompt text.

    Args:
        db_connection_id: Database connection ID
        prompt_text: The user's prompt/question
        storage: Storage instance

    Returns:
        Formatted string of instructions to append to system prompt
    """
    from app.modules.instruction.repositories import InstructionRepository
    from app.utils.model.embedding_model import EmbeddingModel

    instruction_repo = InstructionRepository(storage)

    # Get default instructions (always apply)
    default_instructions = instruction_repo.find_by({
        "db_connection_id": db_connection_id,
        "is_default": "true",
    })

    # Get semantically relevant instructions
    relevant_instructions = []
    try:
        embedding_model = EmbeddingModel().get_model()
        prompt_embedding = embedding_model.embed_query(prompt_text)
        relevant_instructions = instruction_repo.find_by_relevance(
            db_connection_id, prompt_text, prompt_embedding, limit=3
        ) or []
    except Exception:
        # If embedding fails, just use default instructions
        pass

    all_instructions = default_instructions + relevant_instructions

    if not all_instructions:
        return ""

    # Format instructions
    instruction_text = "\n\nCUSTOM INSTRUCTIONS:\n"
    instruction_text += "Follow these specific rules and guidelines:\n\n"

    for i, inst in enumerate(all_instructions, 1):
        if inst.is_default:
            instruction_text += f"{i}. [ALWAYS] {inst.condition}\n   → {inst.rules}\n\n"
        else:
            instruction_text += f"{i}. [WHEN: {inst.condition}]\n   → {inst.rules}\n\n"

    return instruction_text


def get_default_instructions(db_connection_id: str, storage: Storage) -> str:
    """Get only default instructions (for initial system prompt).

    Args:
        db_connection_id: Database connection ID
        storage: Storage instance

    Returns:
        Formatted string of default instructions
    """
    from app.modules.instruction.repositories import InstructionRepository

    instruction_repo = InstructionRepository(storage)

    default_instructions = instruction_repo.find_by({
        "db_connection_id": db_connection_id,
        "is_default": "true",
    })

    if not default_instructions:
        return ""

    instruction_text = "\n\nCUSTOM INSTRUCTIONS (Always Apply):\n"

    for inst in default_instructions:
        instruction_text += f"• {inst.condition}: {inst.rules}\n"

    return instruction_text

from app.modules.prompt.models import Prompt


class NLHistory:
    @staticmethod
    def get_nl_history(prompt: Prompt) -> str:
        if prompt.context:
            history = "\nChat history for Answer:\n"
            for context in prompt.context:
                if context.get("type") == "AI":
                    history += "AI: " + context.get("sql_execution", "") + "\n"
                    history += "AI: " + context.get("nl_generation", "") + "\n"
                elif context.get("type") == "Human":
                    history += "Human: " + context.get("prompt", "") + "\n"
            return history.strip()
        else:
            return None

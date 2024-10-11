from app.modules.prompt.models import Prompt


class SQLHistory:
    @staticmethod
    def get_sql_history(prompt: Prompt) -> str:
        if prompt.context:
            history = """
            #
            Here is Chat histories, use it as context for SQL generation:
            """
            for context in prompt.context:
                if context.get("type") == "AI":
                    history += "AI: " + context.get("sql_generation", "") + "\n"
                elif context.get("type") == "Human":
                    history += "Human: " + context.get("prompt", "") + "\n"
            return history.strip()
        else:
            return ""
from app.modules.prompt.models import Prompt


class QuestionHistory:
    @staticmethod
    def get_question_history(prompt: Prompt) -> str:
        if prompt.context:
            history = """
            #
            Here is AI Agent Chat histories, use it as context for Question generation:
            """
            # TODO: Add context to history
            # for context in prompt.context:
            #     if context.get("type") == "AI":
            #         history += "AI: " + context.get("sql_generation", "") + "\n"
            #     elif context.get("type") == "Human":
            #         history += "Human: " + context.get("prompt", "") + "\n"
            return history.strip()
        else:
            return ""

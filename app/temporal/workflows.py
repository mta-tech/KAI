from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow


@dataclass
class KaiChatInput:
    prompt: str
    connection_id: str
    conversation_id: str | None = None
    callback_url: str | None = None


@workflow.defn
class KaiChatWorkflow:
    @workflow.run
    async def run(self, input: KaiChatInput) -> dict:
        with workflow.unsafe.imports_passed_through():
            from app.temporal.activities import KaiActivities

        result = await workflow.execute_activity_method(
            KaiActivities.chat_streaming,
            args=[
                input.prompt,
                input.connection_id,
                input.conversation_id,
                input.callback_url,
            ],
            start_to_close_timeout=timedelta(minutes=15),
            heartbeat_timeout=timedelta(seconds=60),
        )
        return result

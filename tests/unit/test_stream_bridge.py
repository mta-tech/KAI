import unittest

from app.utils.deep_agent.stream_bridge import bridge_event_to_queue


class DummyQueue:
    def __init__(self):
        self.items = []

    def put(self, value):
        self.items.append(value)


def formatter(text: str) -> str:
    return text.upper()


class StreamBridgeTest(unittest.TestCase):
    def test_bridge_event_outputs_legacy_structure(self):
        queue = DummyQueue()
        event = {
            "todos": [{"status": "pending", "text": "Gather schema"}],
            "tool": {"name": "sql_db_query", "output": "sample"},
            "messages": [{"content": "thinking"}],
            "output": "select * from t",
        }

        bridge_event_to_queue(
            event=event,
            queue=queue,
            format_fn=formatter,
            include_tool_name=False,
        )

        self.assertIn("**Plan Update**", queue.items[0])
        self.assertIn("**Observation:**", queue.items[1])
        self.assertIn("SAMPLE", queue.items[1])
        self.assertIn("**Thought**", queue.items[2])
        self.assertIn("THINKING", queue.items[2])
        self.assertIn("**Final Answer:**", queue.items[3])
        self.assertIn("SELECT * FROM T", queue.items[3])


if __name__ == "__main__":
    unittest.main()


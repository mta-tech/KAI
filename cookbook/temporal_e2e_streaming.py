"""End-to-end test script for the Temporal streaming workflow.

This script exercises the full KAI Temporal streaming pipeline:
  1. Connects to a Temporal server.
  2. Generates a unique session ID and builds a callback URL for the SSE
     receiver.
  3. Subscribes to the SSE stream in a background asyncio task so events
     are captured in real time as the workflow executes.
  4. Starts ``KaiChatWorkflow`` via the Temporal Python SDK.
  5. Waits for the workflow to complete, then validates the result and
     summarises the collected SSE events.

Prerequisites
-------------
Before running this script, ensure the following services are up and
accessible:

1. **Temporal server** (local dev mode)::

       temporal server start-dev

2. **SSE callback receiver** (port 8092)::

       uv run python -m app.temporal.sse_callback

3. **KAI Temporal worker** (registers workflow + activities)::

       uv run python -m app.worker_main

4. **Typesense** (vector/document storage)::

       docker compose up typesense -d

5. **PostgreSQL** with the target dataset accessible and the database
   connection already registered in KAI::

       uv run kai connection create "postgresql://user:pass@host:5432/db" -a mydb

Usage
-----
::

    uv run python cookbook/temporal_e2e_streaming.py \\
        --connection-id <your-connection-id> \\
        --prompt "Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi" \\
        --temporal-host localhost:7233 \\
        --callback-host http://localhost:8092
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import uuid
from datetime import datetime

import httpx
from temporalio.client import Client

from app.temporal.workflows import KaiChatInput, KaiChatWorkflow

# ---------------------------------------------------------------------------
# SSE stream consumer
# ---------------------------------------------------------------------------


async def consume_sse_stream(
    stream_url: str,
    events: list[dict],
    stop_event: asyncio.Event,
) -> None:
    """Consume an SSE stream and append parsed events to *events*.

    Reads ``text/event-stream`` formatted lines from *stream_url* using an
    httpx streaming GET request. Each data payload is parsed as JSON and
    appended to *events*. Prints each event to stdout with a timestamp as it
    arrives.

    The coroutine exits when:
    - A ``done`` or ``timeout`` event type is received.
    - *stop_event* is set externally (e.g. after workflow completion).
    - The HTTP connection is closed or an error occurs.

    Args:
        stream_url: Full URL of the SSE ``/stream/{session_id}`` endpoint.
        events: Mutable list to which received event dicts are appended.
        stop_event: An ``asyncio.Event`` that, when set, signals the consumer
            to stop reading.
    """
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", stream_url) as response:
                response.raise_for_status()
                event_type: str = "message"
                async for raw_line in response.aiter_lines():
                    if stop_event.is_set():
                        break

                    raw_line = raw_line.strip()
                    if not raw_line:
                        # blank line — SSE event boundary, reset type
                        event_type = "message"
                        continue

                    if raw_line.startswith("event:"):
                        event_type = raw_line[len("event:"):].strip()
                        continue

                    if raw_line.startswith("data:"):
                        payload_str = raw_line[len("data:"):].strip()
                        try:
                            payload = json.loads(payload_str)
                        except json.JSONDecodeError:
                            payload = {"raw": payload_str}

                        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        event_label = payload.get("type", event_type)
                        print(f"[{ts}] SSE event type={event_label!r}: {json.dumps(payload, ensure_ascii=False)[:200]}")

                        events.append(payload)

                        # Terminal events — no more data will arrive
                        if event_label in ("done", "timeout"):
                            break
    except httpx.HTTPStatusError as exc:
        print(f"[SSE] HTTP error {exc.response.status_code} while reading stream: {exc}", file=sys.stderr)
    except httpx.RequestError as exc:
        print(f"[SSE] Request error while reading stream: {exc}", file=sys.stderr)
    except asyncio.CancelledError:
        pass  # normal shutdown


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_result(result: dict) -> list[str]:
    """Validate the workflow result dict.

    Checks:
    - ``result["status"]`` is not ``"failed"``.
    - ``result["final_answer"]`` is a non-empty string.
    - ``result["sql_queries"]`` (when present) is a non-empty list.

    Args:
        result: The dict returned by ``KaiChatWorkflow.run``.

    Returns:
        A list of validation failure messages. An empty list means all checks
        passed.
    """
    failures: list[str] = []

    status = result.get("status")
    if status == "failed":
        failures.append(f"Workflow reported status='failed'. error={result.get('error')!r}")

    final_answer = result.get("final_answer")
    if not isinstance(final_answer, str) or not final_answer.strip():
        failures.append(
            f"Expected non-empty 'final_answer' string, got {final_answer!r}"
        )

    sql_queries = result.get("sql_queries")
    if sql_queries is not None and not sql_queries:
        failures.append(
            "Expected 'sql_queries' to be a non-empty list when present, but got an empty list."
        )

    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def run(
    connection_id: str,
    prompt: str,
    temporal_host: str,
    callback_host: str,
) -> None:
    """Execute the end-to-end Temporal streaming test.

    Args:
        connection_id: KAI database connection ID to query against.
        prompt: Natural language query to send to the workflow.
        temporal_host: ``host:port`` of the Temporal frontend service.
        callback_host: Base URL of the SSE callback receiver (e.g.
            ``http://localhost:8092``).
    """
    session_id = f"e2e-test-{uuid.uuid4().hex[:8]}"
    callback_url = f"{callback_host}/events/{session_id}"
    stream_url = f"{callback_host}/stream/{session_id}"
    workflow_id = f"e2e-{session_id}"

    print("=" * 70)
    print("KAI Temporal E2E Streaming Test")
    print("=" * 70)
    print(f"Session ID     : {session_id}")
    print(f"Workflow ID    : {workflow_id}")
    print(f"Connection ID  : {connection_id}")
    print(f"Prompt         : {prompt}")
    print(f"Temporal host  : {temporal_host}")
    print(f"Callback URL   : {callback_url}")
    print(f"SSE stream URL : {stream_url}")
    print("=" * 70)
    print()

    # Connect to Temporal
    print("[init] Connecting to Temporal server ...")
    client = await Client.connect(temporal_host)
    print("[init] Connected.\n")

    # Shared state for SSE consumer
    sse_events: list[dict] = []
    stop_event = asyncio.Event()

    # Start SSE consumer in background — it begins listening before the
    # workflow is submitted so no early events are missed.
    print("[stream] Starting SSE consumer background task ...")
    sse_task = asyncio.create_task(
        consume_sse_stream(stream_url, sse_events, stop_event)
    )

    # Give the SSE consumer a brief moment to establish the HTTP connection
    # before the workflow starts posting events.
    await asyncio.sleep(0.3)

    print("[workflow] Starting KaiChatWorkflow ...\n")
    start_time = time.monotonic()

    try:
        result: dict = await client.execute_workflow(
            KaiChatWorkflow.run,
            KaiChatInput(
                prompt=prompt,
                connection_id=connection_id,
                conversation_id=session_id,
                callback_url=callback_url,
            ),
            id=workflow_id,
            task_queue="kai-agent-queue",
        )
    finally:
        elapsed = time.monotonic() - start_time
        # Signal the SSE consumer to stop and wait for it to finish draining
        # any remaining buffered events.
        stop_event.set()
        try:
            await asyncio.wait_for(sse_task, timeout=5.0)
        except asyncio.TimeoutError:
            sse_task.cancel()

    print()
    print("=" * 70)
    print("Workflow completed")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    failures = validate_result(result)
    if sse_events:
        print(f"[validation] SSE events received  : {len(sse_events)}  (PASS)")
    else:
        failures.append("No SSE events were received during workflow execution.")
        print("[validation] SSE events received  : 0  (FAIL)")

    if failures:
        print("\n[FAIL] Validation errors:")
        for i, msg in enumerate(failures, 1):
            print(f"  {i}. {msg}")
    else:
        print("[PASS] All validations passed.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    final_answer: str = result.get("final_answer") or ""
    sql_queries: list = result.get("sql_queries") or []
    status: str = result.get("status", "unknown")

    print()
    print("Summary")
    print("-" * 70)
    print(f"  Execution time   : {elapsed:.2f}s")
    print(f"  Workflow status  : {status}")
    print(f"  SSE events total : {len(sse_events)}")
    print(f"  SQL queries      : {len(sql_queries)}")
    print(f"  Final answer     : {final_answer[:200]!r}")
    print("-" * 70)

    if failures:
        sys.exit(1)


def main() -> None:
    """Parse CLI arguments and run the E2E test."""
    parser = argparse.ArgumentParser(
        description="End-to-end test for the KAI Temporal streaming workflow.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--connection-id",
        required=True,
        help="KAI database connection ID to use for the query.",
    )
    parser.add_argument(
        "--prompt",
        default=(
            "Tampilkan top 5 provinsi dengan rata-rata modal awal koperasi tertinggi"
        ),
        help="Natural language query to send to the workflow.",
    )
    parser.add_argument(
        "--temporal-host",
        default="localhost:7233",
        help="Temporal frontend host:port.",
    )
    parser.add_argument(
        "--callback-host",
        default="http://localhost:8092",
        help="Base URL of the SSE callback receiver.",
    )

    args = parser.parse_args()

    asyncio.run(
        run(
            connection_id=args.connection_id,
            prompt=args.prompt,
            temporal_host=args.temporal_host,
            callback_host=args.callback_host,
        )
    )


if __name__ == "__main__":
    main()

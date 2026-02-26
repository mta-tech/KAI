"""KAI Temporal Worker with multi-tenant support.

This worker registers with the control plane and processes tasks for a specific organization.
"""

import asyncio
import os
import signal
import socket
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI
from temporalio.client import Client
from temporalio.worker import Worker

from app.temporal.activities import KaiActivities


# Health check server
health_app = FastAPI()
_worker_healthy = False


@health_app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    from fastapi.responses import JSONResponse

    if _worker_healthy:
        return {"status": "healthy"}
    return JSONResponse({"status": "starting"}, status_code=503)


@health_app.get("/readyz")
async def readyz():
    """Readiness check endpoint."""
    from fastapi.responses import JSONResponse

    if _worker_healthy:
        return {"status": "ready"}
    return JSONResponse({"status": "not_ready"}, status_code=503)


async def run_health_server():
    """Run the health check HTTP server."""
    config = uvicorn.Config(
        health_app,
        host="0.0.0.0",
        port=8091,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    await server.serve()


def redact_secret(secret: Optional[str], visible_chars: int = 4) -> str:
    if not secret:
        return "<not set>"
    if len(secret) <= visible_chars:
        return "***"
    return f"{secret[:visible_chars]}{'*' * (len(secret) - visible_chars)}"


class WorkerConfig:
    """Configuration for KAI worker."""

    def __init__(self):
        # Temporal configuration
        self.temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")

        # Organization and multi-tenant configuration
        self.org_id = os.getenv("ORG_ID")
        self.api_key = os.getenv("KAI_API_KEY")

        # Control plane configuration
        self.control_plane_url = os.getenv("CONTROL_PLANE_URL", "http://localhost:8001")
        self.control_plane_api_prefix = os.getenv("CONTROL_PLANE_API_PREFIX", "/services/kcenter")

        # Worker identity
        self.hostname = socket.gethostname()
        self.worker_identity = os.getenv(
            "WORKER_IDENTITY", f"kai-worker-{self.hostname}-{uuid.uuid4().hex[:8]}"
        )

        # Heartbeat configuration
        self.heartbeat_interval_seconds = int(
            os.getenv("HEARTBEAT_INTERVAL_SECONDS", "15")
        )

    @property
    def task_queue(self) -> str:
        """Get the task queue name.

        If ORG_ID is set, returns org-specific queue.
        Otherwise, returns default queue.
        """
        default_queue = os.getenv("TEMPORAL_TASK_QUEUE", "kai-agent-queue")
        if self.org_id:
            return f"kai-{self.org_id}-queue"
        return default_queue

    @property
    def is_multi_tenant(self) -> bool:
        """Check if running in multi-tenant mode."""
        return bool(self.org_id and self.api_key)


class WorkerRegistry:
    """Handles worker registration and heartbeat with the control plane."""

    def __init__(self, config: WorkerConfig):
        self.config = config
        self.worker_id: Optional[str] = None
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def register(self) -> str:
        """Register worker with the control plane.

        Returns:
            The assigned worker ID
        """
        if not self.config.is_multi_tenant:
            print("Not in multi-tenant mode, skipping registration")
            return ""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.control_plane_url}{self.config.control_plane_api_prefix}/v4/kai/worker/register",
                json={
                    "task_queue": self.config.task_queue,
                    "hostname": self.config.hostname,
                    "worker_identity": self.config.worker_identity,
                    "metadata": {
                        "temporal_host": self.config.temporal_host,
                    },
                },
                headers={"X-Org-Api-Key": self.config.api_key or ""},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            self.worker_id = data["worker_id"]
            print(f"Registered with control plane")
            print(f"  Worker ID: {self.worker_id}")
            print(f"  Task Queue: {self.config.task_queue}")
            return self.worker_id or ""

    async def heartbeat(self, active_sessions: int = 0) -> bool:
        """Send heartbeat to the control plane.

        Args:
            active_sessions: Number of currently active sessions

        Returns:
            True if heartbeat successful
        """
        if not self.worker_id:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.control_plane_url}{self.config.control_plane_api_prefix}/v4/kai/worker/{self.worker_id}/heartbeat",
                    json={"active_sessions": active_sessions},
                    headers={"X-Org-Api-Key": self.config.api_key or ""},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Heartbeat failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect worker from the control plane (graceful shutdown).

        Returns:
            True if disconnect successful
        """
        if not self.worker_id:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.control_plane_url}{self.config.control_plane_api_prefix}/v4/kai/worker/{self.worker_id}/disconnect",
                    headers={"X-Org-Api-Key": self.config.api_key or ""},
                    timeout=10.0,
                )
                print(f"Disconnected from control plane: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            print(f"Disconnect failed: {e}")
            return False

    async def start_heartbeat_loop(self):
        """Start the background heartbeat loop."""
        if not self.config.is_multi_tenant:
            return

        self._running = True

        async def heartbeat_loop():
            while self._running:
                await asyncio.sleep(self.config.heartbeat_interval_seconds)
                if self._running:
                    await self.heartbeat()

        self._heartbeat_task = asyncio.create_task(heartbeat_loop())
        print(
            f"Started heartbeat loop (interval: {self.config.heartbeat_interval_seconds}s)"
        )

    async def stop_heartbeat_loop(self):
        """Stop the background heartbeat loop."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass


@asynccontextmanager
async def managed_worker(config: WorkerConfig, registry: WorkerRegistry):
    """Context manager for worker lifecycle with registration and cleanup."""
    try:
        # Register with control plane
        if config.is_multi_tenant:
            await registry.register()
            await registry.start_heartbeat_loop()

        yield

    finally:
        # Cleanup
        if config.is_multi_tenant:
            await registry.stop_heartbeat_loop()
            await registry.disconnect()


async def main():
    """Main entry point for the KAI Temporal worker."""
    global _worker_healthy

    config = WorkerConfig()
    registry = WorkerRegistry(config)

    print(f"KAI Worker Configuration:")
    print(f"  Temporal Host: {config.temporal_host}")
    print(f"  Task Queue: {config.task_queue}")
    print(f"  Multi-tenant: {config.is_multi_tenant}")
    if config.is_multi_tenant:
        print(f"  Org ID: {config.org_id}")
        print(f"  API Key: {redact_secret(config.api_key)}")
        print(f"  Worker Identity: {config.worker_identity}")

    # Start health server in background
    print(f"\nStarting health server on port 8091...")
    health_task = asyncio.create_task(run_health_server())

    # Connect to Temporal
    print(f"Connecting to Temporal at {config.temporal_host}...")
    client = await Client.connect(config.temporal_host)

    # Initialize activities
    activities = KaiActivities()

    # Create worker
    worker = Worker(
        client,
        task_queue=config.task_queue,
        activities=[
            activities.store_connection,
            activities.test_connection,
            activities.scan_schema,
            activities.chat,
            activities.sync_config,
            activities.generate_mdl,
        ],
    )

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def handle_signal(sig):
        print(f"\nReceived signal {sig}, initiating graceful shutdown...")
        shutdown_event.set()

    # Register signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))

    # Run worker with lifecycle management
    async with managed_worker(config, registry):
        print(f"\nStarting KAI Temporal Worker on queue '{config.task_queue}'...")

        # Mark as healthy once worker starts
        _worker_healthy = True
        print("Worker is healthy and ready to process tasks")

        # Run worker until shutdown signal
        worker_task = asyncio.create_task(worker.run())

        # Wait for shutdown signal
        await shutdown_event.wait()

        # Graceful shutdown
        _worker_healthy = False
        print("Shutting down worker...")
        for task in (worker_task, health_task):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    print("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

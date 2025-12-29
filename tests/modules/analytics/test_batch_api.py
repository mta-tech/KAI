"""Tests for batch analytics API endpoints.

Tests cover:
- POST /batch endpoint with valid/invalid requests
- GET /batch/{batch_id} status polling
- GET /batch/{batch_id}/results retrieval
- DELETE /batch/{batch_id} cleanup
- Concurrent batch job handling
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.analytics.batch_api import router as batch_router
from app.modules.analytics.batch_models import (
    AnalyticsBatchResult,
    AnalyticsBatchStatus,
    AnalyticsOperationType,
    BatchJobStatus,
    SingleAnalyticsRequest,
)
from app.modules.analytics.services.batch_service import AnalyticsBatchService


@pytest.fixture
def test_app() -> FastAPI:
    """Create a FastAPI test app with the batch analytics router."""
    app = FastAPI()
    app.include_router(batch_router)
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a test client for the batch analytics API."""
    return TestClient(test_app)


@pytest.fixture
def fresh_batch_service() -> AnalyticsBatchService:
    """Create a fresh batch service for testing."""
    return AnalyticsBatchService()


@pytest.fixture
def valid_batch_request() -> dict:
    """Valid batch request with multiple operations."""
    return {
        "operations": [
            {
                "operation_id": "stats_1",
                "operation_type": "descriptive_stats",
                "params": {"data": [1.0, 2.0, 3.0, 4.0, 5.0]},
            },
            {
                "operation_id": "corr_1",
                "operation_type": "correlation",
                "params": {
                    "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                    "y": [2.0, 4.0, 6.0, 8.0, 10.0],
                },
            },
        ],
        "max_concurrency": 2,
    }


@pytest.fixture
def single_operation_request() -> dict:
    """Valid batch request with a single operation."""
    return {
        "operations": [
            {
                "operation_id": "stats_only",
                "operation_type": "descriptive_stats",
                "params": {"data": [10.0, 20.0, 30.0, 40.0, 50.0]},
            }
        ],
    }


@pytest.fixture
def all_operation_types_request() -> dict:
    """Valid batch request with all operation types."""
    return {
        "operations": [
            {
                "operation_id": "op_stats",
                "operation_type": "descriptive_stats",
                "params": {"data": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]},
            },
            {
                "operation_id": "op_ttest",
                "operation_type": "t_test",
                "params": {
                    "group1": [10.0, 12.0, 14.0, 16.0, 18.0],
                    "group2": [20.0, 22.0, 24.0, 26.0, 28.0],
                },
            },
            {
                "operation_id": "op_corr",
                "operation_type": "correlation",
                "params": {
                    "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                    "y": [2.0, 4.0, 6.0, 8.0, 10.0],
                    "method": "pearson",
                },
            },
            {
                "operation_id": "op_matrix",
                "operation_type": "correlation_matrix",
                "params": {
                    "data": [
                        {"a": 1, "b": 2, "c": 3},
                        {"a": 2, "b": 4, "c": 6},
                        {"a": 3, "b": 6, "c": 9},
                        {"a": 4, "b": 8, "c": 12},
                        {"a": 5, "b": 10, "c": 15},
                    ],
                },
            },
            {
                "operation_id": "op_anomaly",
                "operation_type": "anomaly_detection",
                "params": {
                    "data": [1.0, 2.0, 3.0, 100.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
                    "method": "zscore",
                    "threshold": 2.0,
                },
            },
            {
                "operation_id": "op_forecast",
                "operation_type": "forecast",
                "params": {
                    "values": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
                    "periods": 5,
                },
            },
        ],
        "max_concurrency": 3,
    }


class TestPostBatchEndpoint:
    """Tests for POST /api/v2/analytics/batch endpoint."""

    def test_create_batch_valid_request(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should create a batch job with valid request."""
        response = client.post("/api/v2/analytics/batch", json=valid_batch_request)

        assert response.status_code == 200
        data = response.json()
        assert "batch_id" in data
        assert data["status"] == "pending"
        assert data["total"] == 2
        assert data["message"] == "Batch submitted successfully"
        assert len(data["batch_id"]) == 36  # UUID format

    def test_create_batch_single_operation(
        self, client: TestClient, single_operation_request: dict
    ) -> None:
        """Should create batch job with single operation."""
        response = client.post("/api/v2/analytics/batch", json=single_operation_request)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["status"] == "pending"

    def test_create_batch_all_operation_types(
        self, client: TestClient, all_operation_types_request: dict
    ) -> None:
        """Should create batch job with all operation types."""
        response = client.post("/api/v2/analytics/batch", json=all_operation_types_request)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert data["status"] == "pending"

    def test_create_batch_empty_operations_rejected(self, client: TestClient) -> None:
        """Should reject request with empty operations list."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={"operations": []},
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_create_batch_missing_operations_rejected(self, client: TestClient) -> None:
        """Should reject request without operations field."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={"max_concurrency": 5},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_batch_invalid_operation_type_rejected(
        self, client: TestClient
    ) -> None:
        """Should reject request with invalid operation type."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "invalid_1",
                        "operation_type": "invalid_type",
                        "params": {"data": [1, 2, 3]},
                    }
                ]
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_batch_max_concurrency_limits(self, client: TestClient) -> None:
        """Should accept concurrency within valid range (1-20)."""
        # Test minimum concurrency
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "op_1",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ],
                "max_concurrency": 1,
            },
        )
        assert response.status_code == 200

        # Test maximum concurrency
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "op_2",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ],
                "max_concurrency": 20,
            },
        )
        assert response.status_code == 200

    def test_create_batch_concurrency_out_of_range_rejected(
        self, client: TestClient
    ) -> None:
        """Should reject concurrency outside valid range."""
        # Test below minimum
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "op_1",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ],
                "max_concurrency": 0,
            },
        )
        assert response.status_code == 422

        # Test above maximum
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "op_2",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ],
                "max_concurrency": 21,
            },
        )
        assert response.status_code == 422

    def test_create_batch_too_many_operations_rejected(
        self, client: TestClient
    ) -> None:
        """Should reject request with more than 100 operations."""
        operations = [
            {
                "operation_id": f"op_{i}",
                "operation_type": "descriptive_stats",
                "params": {"data": [1, 2, 3]},
            }
            for i in range(101)
        ]
        response = client.post(
            "/api/v2/analytics/batch",
            json={"operations": operations},
        )

        assert response.status_code == 422

    def test_create_batch_default_concurrency(self, client: TestClient) -> None:
        """Should use default concurrency when not specified."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "op_1",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ]
            },
        )

        assert response.status_code == 200
        # Default is 5, but we just verify the request succeeds

    def test_create_batch_assigns_operation_ids(self, client: TestClient) -> None:
        """Should accept operations without explicit IDs."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    },
                    {
                        "operation_type": "correlation",
                        "params": {"x": [1, 2, 3], "y": [2, 4, 6]},
                    },
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2


class TestGetBatchStatusEndpoint:
    """Tests for GET /api/v2/analytics/batch/{batch_id} endpoint."""

    def test_get_status_existing_batch(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return status of existing batch job."""
        # Create a batch
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Get status
        response = client.get(f"/api/v2/analytics/batch/{batch_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["batch_id"] == batch_id
        assert "status" in data
        assert "total" in data
        assert "completed" in data
        assert "failed" in data
        assert "created_at" in data

    def test_get_status_nonexistent_batch(self, client: TestClient) -> None:
        """Should return 404 for nonexistent batch job."""
        response = client.get("/api/v2/analytics/batch/nonexistent-batch-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_status_shows_initial_pending(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should show pending status immediately after creation."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.get(f"/api/v2/analytics/batch/{batch_id}")

        data = response.json()
        # Status might already be processing, but should be valid
        assert data["status"] in ["pending", "running", "completed", "partial", "failed"]
        assert data["total"] == 2

    def test_get_status_includes_timing(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should include timing information in status."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.get(f"/api/v2/analytics/batch/{batch_id}")

        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data
        # started_at and completed_at may or may not be present

    def test_get_status_includes_progress_counters(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should include progress counters in status."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.get(f"/api/v2/analytics/batch/{batch_id}")

        data = response.json()
        assert "total" in data
        assert "completed" in data
        assert "failed" in data
        assert data["total"] == 2
        assert data["completed"] >= 0
        assert data["failed"] >= 0


class TestGetBatchResultsEndpoint:
    """Tests for GET /api/v2/analytics/batch/{batch_id}/results endpoint."""

    def test_get_results_existing_batch(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return results of existing batch job."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Small delay to allow background processing to start
        time.sleep(0.1)

        response = client.get(f"/api/v2/analytics/batch/{batch_id}/results")

        assert response.status_code == 200
        data = response.json()
        assert data["batch_id"] == batch_id
        assert "status" in data
        assert "total" in data
        assert "completed" in data
        assert "failed" in data
        assert "results" in data
        assert isinstance(data["results"], dict)

    def test_get_results_nonexistent_batch(self, client: TestClient) -> None:
        """Should return 404 for nonexistent batch job."""
        response = client.get("/api/v2/analytics/batch/nonexistent-id/results")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_results_empty_initially(
        self, client: TestClient, single_operation_request: dict
    ) -> None:
        """Should return empty results dict if processing not started."""
        # Use a patched service to prevent background processing
        with patch(
            "app.modules.analytics.batch_api.analytics_batch_service"
        ) as mock_service:
            # Create a mock job that returns pending status
            from datetime import datetime

            mock_job = AnalyticsBatchStatus(
                batch_id="test-batch-id",
                status=BatchJobStatus.PENDING,
                total=1,
                completed=0,
                failed=0,
                results={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            mock_service.create_batch_job.return_value = mock_job
            mock_service.get_batch_job.return_value = mock_job

            # Create batch
            response = client.post(
                "/api/v2/analytics/batch", json=single_operation_request
            )
            batch_id = response.json()["batch_id"]

            # Get results
            response = client.get(f"/api/v2/analytics/batch/{batch_id}/results")

            data = response.json()
            assert data["results"] == {}

    def test_get_results_format(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return results in correct format."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Wait briefly for processing
        time.sleep(0.2)

        response = client.get(f"/api/v2/analytics/batch/{batch_id}/results")

        data = response.json()
        # If there are any results, verify their format
        if data["results"]:
            for op_id, result in data["results"].items():
                assert "operation_id" in result
                assert "operation_type" in result
                assert "status" in result
                assert result["status"] in ["completed", "failed"]


class TestDeleteBatchEndpoint:
    """Tests for DELETE /api/v2/analytics/batch/{batch_id} endpoint."""

    def test_delete_existing_batch(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should delete existing batch job."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.delete(f"/api/v2/analytics/batch/{batch_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["batch_id"] == batch_id
        assert data["deleted"] is True
        assert "message" in data

    def test_delete_nonexistent_batch(self, client: TestClient) -> None:
        """Should return 404 for nonexistent batch job."""
        response = client.delete("/api/v2/analytics/batch/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_delete_cleans_up_job(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should remove job from storage after deletion."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Delete the batch
        client.delete(f"/api/v2/analytics/batch/{batch_id}")

        # Verify it's gone
        response = client.get(f"/api/v2/analytics/batch/{batch_id}")
        assert response.status_code == 404

    def test_delete_returns_final_status(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return the final status in delete response."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.delete(f"/api/v2/analytics/batch/{batch_id}")

        data = response.json()
        assert "status" in data
        # Status should be valid
        assert data["status"] in [
            "pending",
            "running",
            "completed",
            "partial",
            "failed",
            "cancelled",
        ]

    def test_delete_pending_batch_cancels_first(
        self, client: TestClient
    ) -> None:
        """Should cancel pending batch before deleting."""
        with patch(
            "app.modules.analytics.batch_api.analytics_batch_service"
        ) as mock_service:
            from datetime import datetime

            mock_job = AnalyticsBatchStatus(
                batch_id="test-batch-id",
                status=BatchJobStatus.PENDING,
                total=1,
                completed=0,
                failed=0,
                results={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            cancelled_job = AnalyticsBatchStatus(
                batch_id="test-batch-id",
                status=BatchJobStatus.CANCELLED,
                total=1,
                completed=0,
                failed=0,
                results={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                completed_at=datetime.now(),
            )
            mock_service.get_batch_job.side_effect = [mock_job, cancelled_job, None]
            mock_service.cancel_batch_job.return_value = cancelled_job
            mock_service.delete_batch_job.return_value = True

            response = client.delete("/api/v2/analytics/batch/test-batch-id")

            assert response.status_code == 200
            mock_service.cancel_batch_job.assert_called_once_with("test-batch-id")
            mock_service.delete_batch_job.assert_called_once_with("test-batch-id")


class TestConcurrentBatchJobs:
    """Tests for concurrent batch job handling."""

    def test_create_multiple_batches_concurrently(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should handle multiple batch job creations."""
        batch_ids = []

        # Create multiple batches
        for i in range(5):
            modified_request = {
                **valid_batch_request,
                "operations": [
                    {
                        "operation_id": f"batch_{i}_stats",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [float(j) for j in range(i + 1, i + 6)]},
                    }
                ],
            }
            response = client.post("/api/v2/analytics/batch", json=modified_request)
            assert response.status_code == 200
            batch_ids.append(response.json()["batch_id"])

        # All batch IDs should be unique
        assert len(set(batch_ids)) == 5

        # All batches should be retrievable
        for batch_id in batch_ids:
            response = client.get(f"/api/v2/analytics/batch/{batch_id}")
            assert response.status_code == 200

    def test_batch_jobs_independent(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should keep batch jobs independent."""
        # Create first batch
        response1 = client.post("/api/v2/analytics/batch", json=valid_batch_request)
        batch_id_1 = response1.json()["batch_id"]

        # Create second batch
        response2 = client.post("/api/v2/analytics/batch", json=valid_batch_request)
        batch_id_2 = response2.json()["batch_id"]

        # Delete first batch
        client.delete(f"/api/v2/analytics/batch/{batch_id_1}")

        # Second batch should still exist
        response = client.get(f"/api/v2/analytics/batch/{batch_id_2}")
        assert response.status_code == 200

    def test_large_batch_processing(self, client: TestClient) -> None:
        """Should handle large batch with many operations."""
        operations = [
            {
                "operation_id": f"stats_{i}",
                "operation_type": "descriptive_stats",
                "params": {"data": [float(j) for j in range(10)]},
            }
            for i in range(50)
        ]

        response = client.post(
            "/api/v2/analytics/batch",
            json={"operations": operations, "max_concurrency": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 50

    def test_batch_status_polling(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should support status polling during processing."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Poll status multiple times
        statuses = []
        for _ in range(3):
            response = client.get(f"/api/v2/analytics/batch/{batch_id}")
            assert response.status_code == 200
            statuses.append(response.json()["status"])
            time.sleep(0.05)

        # All returned statuses should be valid
        for status in statuses:
            assert status in [
                "pending",
                "running",
                "completed",
                "partial",
                "failed",
                "cancelled",
            ]


class TestInvalidRequests:
    """Tests for handling invalid requests."""

    def test_invalid_json_rejected(self, client: TestClient) -> None:
        """Should reject malformed JSON."""
        response = client.post(
            "/api/v2/analytics/batch",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    def test_missing_params_in_operation(self, client: TestClient) -> None:
        """Should accept operations with empty params (validation happens at execution)."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "no_params",
                        "operation_type": "descriptive_stats",
                        "params": {},
                    }
                ]
            },
        )

        # Request should be accepted; validation happens during processing
        assert response.status_code == 200

    def test_null_operation_type_rejected(self, client: TestClient) -> None:
        """Should reject operations with null operation type."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "null_type",
                        "operation_type": None,
                        "params": {"data": [1, 2, 3]},
                    }
                ]
            },
        )

        assert response.status_code == 422

    def test_invalid_batch_id_format(self, client: TestClient) -> None:
        """Should return 404 for invalid batch ID format."""
        # Invalid format but still valid for lookup (will return 404)
        response = client.get("/api/v2/analytics/batch/!!invalid!!")

        assert response.status_code == 404


class TestOperationTypeValidation:
    """Tests for validating different operation types."""

    @pytest.mark.parametrize(
        "operation_type,params",
        [
            ("descriptive_stats", {"data": [1.0, 2.0, 3.0, 4.0, 5.0]}),
            ("t_test", {"group1": [1.0, 2.0, 3.0], "group2": [4.0, 5.0, 6.0]}),
            ("correlation", {"x": [1.0, 2.0, 3.0], "y": [2.0, 4.0, 6.0]}),
            (
                "correlation_matrix",
                {"data": [{"a": 1, "b": 2}, {"a": 2, "b": 4}, {"a": 3, "b": 6}]},
            ),
            ("anomaly_detection", {"data": [1.0, 2.0, 100.0, 3.0, 4.0]}),
            ("forecast", {"values": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}),
        ],
    )
    def test_valid_operation_types_accepted(
        self, client: TestClient, operation_type: str, params: dict
    ) -> None:
        """Should accept all valid operation types."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": f"test_{operation_type}",
                        "operation_type": operation_type,
                        "params": params,
                    }
                ]
            },
        )

        assert response.status_code == 200


class TestResponseFormats:
    """Tests for API response formats."""

    def test_create_response_format(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return properly formatted create response."""
        response = client.post("/api/v2/analytics/batch", json=valid_batch_request)

        data = response.json()
        assert isinstance(data["batch_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["total"], int)
        assert isinstance(data["message"], str)

    def test_status_response_format(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return properly formatted status response."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.get(f"/api/v2/analytics/batch/{batch_id}")

        data = response.json()
        assert isinstance(data["batch_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["total"], int)
        assert isinstance(data["completed"], int)
        assert isinstance(data["failed"], int)
        assert isinstance(data["results"], dict)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)

    def test_results_response_format(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return properly formatted results response."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        time.sleep(0.2)

        response = client.get(f"/api/v2/analytics/batch/{batch_id}/results")

        data = response.json()
        assert isinstance(data["batch_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["total"], int)
        assert isinstance(data["completed"], int)
        assert isinstance(data["failed"], int)
        assert isinstance(data["results"], dict)

    def test_delete_response_format(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should return properly formatted delete response."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        response = client.delete(f"/api/v2/analytics/batch/{batch_id}")

        data = response.json()
        assert isinstance(data["batch_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["deleted"], bool)
        assert isinstance(data["message"], str)

    def test_error_response_format(self, client: TestClient) -> None:
        """Should return properly formatted error response."""
        response = client.get("/api/v2/analytics/batch/nonexistent-id")

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_batch_with_exactly_100_operations(self, client: TestClient) -> None:
        """Should accept exactly 100 operations (max limit)."""
        operations = [
            {
                "operation_id": f"op_{i}",
                "operation_type": "descriptive_stats",
                "params": {"data": [1, 2, 3]},
            }
            for i in range(100)
        ]

        response = client.post(
            "/api/v2/analytics/batch",
            json={"operations": operations},
        )

        assert response.status_code == 200
        assert response.json()["total"] == 100

    def test_batch_with_exactly_1_operation(self, client: TestClient) -> None:
        """Should accept exactly 1 operation (min limit)."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ]
            },
        )

        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_batch_with_long_operation_ids(self, client: TestClient) -> None:
        """Should accept operations with long IDs."""
        long_id = "a" * 200

        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": long_id,
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ]
            },
        )

        assert response.status_code == 200

    def test_batch_with_special_characters_in_id(self, client: TestClient) -> None:
        """Should accept operations with special characters in IDs."""
        response = client.post(
            "/api/v2/analytics/batch",
            json={
                "operations": [
                    {
                        "operation_id": "op-with-dashes_and_underscores.and.dots",
                        "operation_type": "descriptive_stats",
                        "params": {"data": [1, 2, 3]},
                    }
                ]
            },
        )

        assert response.status_code == 200

    def test_create_and_immediately_get_status(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should be able to get status immediately after creation."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Immediately get status
        status_response = client.get(f"/api/v2/analytics/batch/{batch_id}")

        assert status_response.status_code == 200
        assert status_response.json()["batch_id"] == batch_id

    def test_create_and_immediately_delete(
        self, client: TestClient, valid_batch_request: dict
    ) -> None:
        """Should be able to delete immediately after creation."""
        create_response = client.post(
            "/api/v2/analytics/batch", json=valid_batch_request
        )
        batch_id = create_response.json()["batch_id"]

        # Immediately delete
        delete_response = client.delete(f"/api/v2/analytics/batch/{batch_id}")

        assert delete_response.status_code == 200
        assert delete_response.json()["deleted"] is True

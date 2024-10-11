import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch



@patch('app.api.API.create_database_connection')  # Adjust import path as necessary
def test_create_database_connection(mock_create_db_connection):
    # Configure the mock to return a dummy response
    mock_create_db_connection.return_value = {
        "id": "test-id",
        "alias": "service_instances",
        "dialect": "postgresql",
        "connection_uri": "postgresql://myuser:mypassword@localhost:15432/mydatabase",
        "schemas": ["public"],
        "metadata": {},
        "created_at": "2024-09-11T00:00:00Z"
    }
    client = TestClient(app)
    payload = {
        "alias": "service_instances",
        "connection_uri": "postgresql://myuser:mypassword@localhost:15432/mydatabase",
        "schemas": ["public"],
        "metadata": {}
    }
    response = client.post(
        "/api/v1/database-connections",
        json=payload
    )
    print(response.json())

    assert response.status_code == 201
    assert "id" in response.json()
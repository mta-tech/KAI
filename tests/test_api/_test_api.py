import pytest
import fastapi
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.data.db.storage import Storage
from app.api import API
from app.modules.database_connection.models import DatabaseConnection

@pytest.fixture
def client():
    mock_storage = Mock(spec=Storage)
    api = API(mock_storage)
    app = fastapi.FastAPI()
    app.include_router(api.router)
    return TestClient(app), api

def test_create_database_connection_success(client):
    test_client, api = client
    
    # Arrange
    request_data = {
        "name": "Test DB",
        "dialect": "postgresql",
        "host": "localhost",
        "port": 5432,
        "username": "testuser",
        "password": "testpass",
        "database": "testdb"
    }
    api.database_connection_service.create_database_connection.return_value = DatabaseConnection(id="test_id", **request_data)

    # Act
    response = test_client.post("/api/v1/database-connections", json=request_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["id"] == "test_id"
    assert response.json()["name"] == "Test DB"

def test_create_database_connection_validation_error(client):
    test_client, _ = client
    
    # Act
    response = test_client.post("/api/v1/database-connections", json={"name": "Invalid DB"})

    # Assert
    assert response.status_code == 422

def test_create_database_connection_service_error(client):
    test_client, api = client
    
    # Arrange
    api.database_connection_service.create_database_connection.side_effect = Exception("Service error")

    # Act
    response = test_client.post("/api/v1/database-connections", 
                                json={"name": "Test DB", "dialect": "postgresql", "host": "localhost", 
                                      "port": 5432, "username": "testuser", "password": "testpass", "database": "testdb"})

    # Assert
    assert response.status_code == 500
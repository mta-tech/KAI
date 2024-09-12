import pytest
from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app

client = TestClient(app)

@pytest.fixture(scope="module")
def create_database_connection():
    payload = {
        "alias": "dvdrental",
        "connection_uri": "postgresql://myuser:mypassword@localhost:15432/dvdrental",
        "schemas": ["public"],
        "metadata": {}
    }
    response = client.post(
        "/api/v1/database-connections",
        json=payload
    )
    assert response.status_code == 201
    return response.json()["id"]  # Return the "id" from the response

def test_create_database_connection(create_database_connection):
    assert create_database_connection is not None  # Ensure we have the ID

def test_list_database_connections():
    response = client.get("/api/v1/database-connections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "id" in response.json()[0]
        assert "alias" in response.json()[0]
        assert "connection_uri" in response.json()[0]

# def test_delete_database_connection(create_database_connection):
#     # Use the ID obtained from the fixture
#     response = client.delete(f"/api/v1/database-connections/{create_database_connection}")
#     assert response.status_code == 204  # Assuming 204 for a successful delete

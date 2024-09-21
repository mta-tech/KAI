import pytest
from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app

client = TestClient(app)

@pytest.fixture(scope="module")
def list_database_connections():
    response = client.get("/api/v1/database-connections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "id" in response.json()[0]
        assert "alias" in response.json()[0]
        assert "connection_uri" in response.json()[0]
    return response.json()

@pytest.fixture(scope="module")
def list_table_descriptions(list_database_connections):
    db_id = list_database_connections[0]["id"]  # Get the ID of the first connection
    params = {"db_connection_id": db_id}
    response = client.get("/api/v1/table-descriptions", params=params)
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Ensure the response is a list
    if response.json():
        assert "table_name" in response.json()[0]
        assert "columns" in response.json()[0]
    return response.json()[0]  # Return the first item for further use

def test_list_table_descriptions(list_table_descriptions):
    # Use the stored table description data
    table_description = list_table_descriptions
    print(table_description)
    assert "table_name" in table_description
    assert "columns" in table_description
    # Add further assertions or use table_description['id'] for additional tests

def test_sync_schemas(list_table_descriptions):
    table_id = list_table_descriptions["id"]  # Get the ID of the table description
    request_body = {
        "table_description_ids": [table_id],
        "metadata": {}
    }
    
    response = client.post(
        "/api/v1/table-descriptions/sync-schemas",
        json=request_body
    )
    
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
    
    # Add assertions based on your expected response
    assert response.status_code == 201
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app
from app.data.db.storage import Storage
from app.server.config import Settings

@pytest.fixture(scope="session")
def typesense_storage():
    # Initialize storage with settings
    storage = Storage(Settings())

    # Clean up collections before test
    existing_collections = storage._get_existing_collections()
    print(existing_collections)
    for collection in existing_collections:
        storage.delete_collection(collection)
    yield storage  # Provide the storage instance to the test

@pytest.fixture(scope="session")
def client():
    yield TestClient(app)

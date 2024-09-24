import pytest
from unittest.mock import MagicMock
# from fastapi import HTTPException
from app.modules.prompt.services import PromptService
from app.modules.prompt.models import Prompt
from app.api.requests import PromptRequest #, UpdateMetadataRequest
# from app.modules.database_connection.repositories import DatabaseConnectionRepository
# from app.modules.prompt.repositories import PromptRepository

@pytest.fixture
def mock_storage():
    return MagicMock()

@pytest.fixture
def prompt_service(mock_storage):
    return PromptService(mock_storage)

def test_create_prompt(prompt_service, mock_storage):
    # Mock dependencies
    mock_db_connection_repository = MagicMock()
    mock_storage.database_connection_repository = mock_db_connection_repository
    mock_prompt_repository = MagicMock()
    mock_storage.prompt_repository = mock_prompt_repository
    
    # Mock database connection
    mock_db_connection = MagicMock()
    mock_db_connection.id = "db-conn-id"
    mock_db_connection.schemas = []
    mock_db_connection_repository.find_by_id.return_value = mock_db_connection
    
    # Mock prompt insertion
    mock_prompt = Prompt(id="prompt-id", text="Test Prompt", db_connection_id="db-conn-id", schemas=[], metadata={})
    mock_prompt_repository.insert.return_value = mock_prompt

    # Call the method
    prompt_request = PromptRequest(
        text="Test Prompt",
        db_connection_id="db-conn-id",
        schemas=[],
        metadata={}
    )
    result = prompt_service.create_prompt(prompt_request)

    # Assertions
    mock_db_connection_repository.find_by_id.assert_called_once_with("db-conn-id")
    mock_prompt_repository.insert.assert_called_once()
    assert result.id == "prompt-id"
    assert result.text == "Test Prompt"

# def test_get_prompts(prompt_service, mock_storage):
#     # Mock dependencies
#     mock_db_connection_repository = MagicMock()
#     mock_storage.database_connection_repository = mock_db_connection_repository
#     mock_prompt_repository = MagicMock()
#     mock_storage.prompt_repository = mock_prompt_repository

#     # Mock database connection
#     mock_db_connection = MagicMock()
#     mock_db_connection.id = "db-conn-id"
#     mock_db_connection.schemas = []
#     mock_db_connection_repository.find_by_id.return_value = mock_db_connection
    
#     # Mock prompts retrieval
#     mock_prompt = Prompt(id="prompt-id", text="Test Prompt", db_connection_id="db-conn-id", schemas=[], metadata={})
#     mock_prompt_repository.find_by.return_value = [mock_prompt]

#     # Call the method
#     result = prompt_service.get_prompts("db-conn-id")

#     # Assertions
#     mock_db_connection_repository.find_by_id.assert_called_once_with("db-conn-id")
#     mock_prompt_repository.find_by.assert_called_once_with({"db_connection_id": "db-conn-id"})
#     assert len(result) == 1
#     assert result[0].id == "prompt-id"

# def test_update_prompt(prompt_service, mock_storage):
#     # Mock dependencies
#     mock_prompt_repository = MagicMock()
#     mock_storage.prompt_repository = mock_prompt_repository

#     # Mock prompt
#     mock_prompt = Prompt(id="prompt-id", text="Test Prompt", db_connection_id="db-conn-id", schemas=[], metadata={})
#     mock_prompt_repository.find_by_id.return_value = mock_prompt

#     # Mock prompt update
#     updated_prompt = Prompt(id="prompt-id", text="Test Prompt", db_connection_id="db-conn-id", schemas=[], metadata={"new_key": "new_value"})
#     mock_prompt_repository.update.return_value = updated_prompt

#     # Call the method
#     metadata_request = UpdateMetadataRequest(metadata={"new_key": "new_value"})
#     result = prompt_service.update_prompt("prompt-id", metadata_request)

#     # Assertions
#     mock_prompt_repository.find_by_id.assert_called_once_with("prompt-id")
#     mock_prompt_repository.update.assert_called_once()
#     assert result.metadata == {"new_key": "new_value"}

# def test_get_prompt(prompt_service, mock_storage):
#     # Mock dependencies
#     mock_prompt_repository = MagicMock()
#     mock_storage.prompt_repository = mock_prompt_repository

#     # Mock prompt
#     mock_prompt = Prompt(id="prompt-id", text="Test Prompt", db_connection_id="db-conn-id", schemas=[], metadata={})
#     mock_prompt_repository.find_by_id.return_value = mock_prompt

#     # Call the method
#     result = prompt_service.get_prompt("prompt-id")

#     # Assertions
#     mock_prompt_repository.find_by_id.assert_called_once_with("prompt-id")
#     assert result.id == "prompt-id"

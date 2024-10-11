import pytest
from fastapi import HTTPException

# We'll use this fixture to handle imports
@pytest.fixture(autouse=True)
def import_dependencies():
    global PromptRequest, UpdateMetadataRequest, PromptService, Prompt, DatabaseConnectionRepository
    from app.api.requests import PromptRequest, UpdateMetadataRequest
    from app.modules.prompt.services import PromptService
    from app.modules.prompt.models import Prompt
    from app.modules.database_connection.repositories import DatabaseConnectionRepository

@pytest.fixture
def mock_storage():
    from unittest.mock import Mock
    return Mock()

@pytest.fixture
def prompt_service(mock_storage):
    return PromptService(mock_storage)

def test_create_prompt_success(prompt_service):
    from unittest.mock import Mock, patch
    
    # Arrange
    mock_db_connection = Mock()
    mock_db_connection.schemas = True
    mock_db_connection.dialect = "postgresql"

    prompt_service.repository.insert = Mock(return_value=Prompt(id="new_prompt_id"))
    
    with patch.object(DatabaseConnectionRepository, 'find_by_id', return_value=mock_db_connection):
        prompt_request = PromptRequest(
            text="SELECT * FROM users",
            db_connection_id="db_conn_id",
            schemas=["public"],
            metadata={"key": "value"}
        )

        # Act
        result = prompt_service.create_prompt(prompt_request)

        # Assert
        assert isinstance(result, Prompt)
        assert result.id == "new_prompt_id"
        prompt_service.repository.insert.assert_called_once()

# def test_create_prompt_db_connection_not_found(prompt_service):
#     from unittest.mock import patch
    
#     # Arrange
#     with patch.object(DatabaseConnectionRepository, 'find_by_id', return_value=None):
#         prompt_request = PromptRequest(
#             text="SELECT * FROM users",
#             db_connection_id="non_existent_id",
#             schemas=["public"],
#             metadata={"key": "value"}
#         )

#         # Act & Assert
#         with pytest.raises(HTTPException) as exc_info:
#             prompt_service.create_prompt(prompt_request)
#         assert "Database connection non_existent_id not found" in str(exc_info.value)

# # ... (implement other test functions similarly)

# def test_get_prompts_success(prompt_service):
#     from unittest.mock import Mock, patch
    
#     # Arrange
#     mock_db_connection = Mock()
#     mock_prompts = [Prompt(id="prompt1"), Prompt(id="prompt2")]
    
#     with patch.object(DatabaseConnectionRepository, 'find_by_id', return_value=mock_db_connection):
#         prompt_service.repository.find_by = Mock(return_value=mock_prompts)

#         # Act
#         result = prompt_service.get_prompts("db_conn_id")

#         # Assert
#         assert result == mock_prompts
#         prompt_service.repository.find_by.assert_called_once_with({"db_connection_id": "db_conn_id"})

# # ... (implement other test functions similarly)
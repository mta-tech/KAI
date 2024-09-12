import pytest
from unittest.mock import MagicMock, patch
from app.modules.nl_generation.services import NLGenerationService
# from app.modules.nl_generation.models import NLGeneration, LLMConfig
# from app.api.requests import NLGenerationRequest, NLGenerationsSQLGenerationRequest, PromptSQLGenerationNLGenerationRequest
# from app.modules.sql_generation.models import SQLGeneration
# from app.modules.prompt.models import Prompt

@pytest.fixture
def mock_storage():
    return MagicMock()

@pytest.fixture
def nl_generation_service(mock_storage):
    return NLGenerationService(mock_storage)

def test_create_nl_generation(nl_generation_service, mock_storage):
    pass


# def test_create_nl_generation(nl_generation_service, mock_storage):
#     with patch('app.modules.nl_generation.services.GeneratesNlAnswer') as mock_generates_nl_answer:
#         mock_nl_generation_repository = MagicMock()
#         mock_storage.nl_generation_repository = mock_nl_generation_repository
#         mock_sql_generation_repository = MagicMock()
#         mock_storage.sql_generation_repository = mock_sql_generation_repository

#         mock_sql_generation_repository.find_by_id.return_value = SQLGeneration(id="sql-gen-id")
#         mock_generates_nl_answer.return_value.execute.return_value = MagicMock(text="Generated NL Text")

#         nl_generation_request = NLGenerationRequest(llm_config=LLMConfig(), metadata={})
#         result = nl_generation_service.create_nl_generation("sql-gen-id", nl_generation_request)

#         mock_nl_generation_repository.insert.assert_called_once()
#         mock_sql_generation_repository.find_by_id.assert_called_once_with("sql-gen-id")
#         mock_generates_nl_answer.return_value.execute.assert_called_once()
#         assert result.text == "Generated NL Text"

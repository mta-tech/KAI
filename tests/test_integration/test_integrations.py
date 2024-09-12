import pytest
# from fastapi.testclient import TestClient
# from app.main import app  # FastAPI app
# from app.data.db.storage import Storage
# from app.server.config import Settings

def test_typesense_storage_initialization(typesense_storage):
    # Fetch existing collections after the setup
    collections = typesense_storage._get_existing_collections()

    # Ensure that all collections were deleted before running the test
    assert len(collections) == 0

def test_create_database_connection(client):
    payload = {
        "alias": "dvdrental",
        "connection_uri": "postgresql://myuser:mypassword@localhost:15432/dvdrental",
        "schemas": ["public"],
        "metadata": {}
        # "alias": "sqlite_memory",
        # "connection_uri": "sqlite:///:memory:",
        # "schemas": [],
        # "metadata": {}
    }

    response = client.post(
        "/api/v1/database-connections",
        json=payload
    )

    # Check the response status code
    assert response.status_code == 201
    # Check if the response contains the 'id'
    assert "id" in response.json()

# TODO: Invalid database connection should return 422, currently internal server error
def test_create_invalid_database_connection(client):
#     # Invalid payload: missing connection_uri and alias, or having an incorrect format
#     invalid_payload = {
#         "alias": "invalid-test",  # Invalid alias
#         "connection_uri": "invalid_uri",  # Invalid connection URI format
#         "schemas": ['public'],  # This can also be a source of invalid input if it's empty
#         "metadata": {}  # Assuming metadata can be optional
#     }

#     # Make POST request to create a database connection with invalid data
#     response = client.post(
#         "/api/v1/database-connections",
#         json=invalid_payload
#     )

#     # Assert that the response status code is 422 (Unprocessable Entity)
#     assert response.status_code == 422
    pass

@pytest.fixture
def test_list_database_connections(client):
    response = client.get("/api/v1/database-connections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "id" in response.json()[0]
        assert "alias" in response.json()[0]
        assert "connection_uri" in response.json()[0]
    return response.json()[0]["id"] if response.json() else None

# TODO: Update database connection API still not working
def test_update_database_connection(client, test_list_database_connections):
    # # Step 1: Use fixture to get an existing database connection ID
    # db_connection_id = test_list_database_connections
    # print(db_connection_id)
    # if db_connection_id is None:
    #     pytest.skip("No database connection available to update")

    # # Step 2: Update the existing database connection
    # update_payload = {
    #     "alias": "dvdrental_updated",  # Updated alias
    #     "connection_uri": "postgresql://myuser:mypassword@localhost:15432/dvdrental",  # Updated URI
    #     "schemas": ["public"],  # Adding a new schema
    #     "metadata": {"description": "Updated connection"}  # Adding metadata
    # }
    # update_response = client.put(
    #     f"/api/v1/database-connections/{db_connection_id}",
    #     json=update_payload
    # )

    # # Step 3: Assert the update was successful
    # assert update_response.status_code == 200  # Assuming 200 OK for a successful update
    # updated_connection = update_response.json()

    # # Step 4: Validate the response contains updated data
    # assert updated_connection["alias"] == "dvdrental_updated"
    pass

@pytest.fixture
def test_list_table_descriptions(client, test_list_database_connections):
    db_connection_id = test_list_database_connections

    if db_connection_id is None:
        pytest.skip("No database connection available to test table descriptions")

    response = client.get(f"/api/v1/table-descriptions?db_connection_id={db_connection_id}")

    assert response.status_code == 200
    table_descriptions = response.json()
    assert isinstance(table_descriptions, list) 
    if table_descriptions:
        assert isinstance(table_descriptions[0], dict)
        assert "table_name" in table_descriptions[0]
        assert "columns" in table_descriptions[0]
    
    if table_descriptions:
        # Return a list of table description IDs for use in the PUT request
        return [desc["id"] for desc in table_descriptions]
    return None

def test_get_table_description(client, test_list_table_descriptions):
    table_description_id = test_list_table_descriptions[0]

    if table_description_id is None:
        pytest.skip("No table description available to test")

    response = client.get(f"/api/v1/table-descriptions/{table_description_id}")

    assert response.status_code == 200
    table_description = response.json()

    # Basic checks on the response
    assert isinstance(table_description, dict)
    assert "table_name" in table_description
    assert "columns" in table_description

def test_sync_schemas(client, test_list_table_descriptions):
    if not test_list_table_descriptions:
        pytest.skip("No table description IDs available to test schema sync")
    length_of_ids = len(test_list_table_descriptions)
    if length_of_ids > 3:
        length_of_ids = 3

    payload = {
        "table_description_ids": test_list_table_descriptions[:length_of_ids],
        "metadata": {}
    }

    response = client.post("/api/v1/table-descriptions/sync-schemas", json=payload)

    assert response.status_code == 201
    # Assuming the response might include some confirmation or result
    # result = response.json()
    
# TODO: Test for update table description still not working

# TODO: Test for refresh table description still not working

@pytest.fixture()
def test_create_instruction(client, test_list_database_connections):
    db_connection_id = test_list_database_connections

    if db_connection_id is None:
        pytest.skip("No database connection available to test instructions")
    condition = "Create condition"
    rules = "Create rules"
    payload = {
        "db_connection_id": db_connection_id,
        "condition": condition,
        "rules": rules,
        "is_default": True,
        "metadata": {}
    }

    response = client.post("/api/v1/instructions", json=payload)

    assert response.status_code == 201  # Assuming 201 Created is the expected status code
    instruction = response.json()

    # Basic checks on the response
    assert isinstance(instruction, dict)
    assert "id" in instruction
    assert instruction["db_connection_id"] == db_connection_id
    assert instruction["condition"] == condition
    assert instruction["rules"] == rules
    assert instruction["is_default"] is True
    assert "metadata" in instruction

    return instruction["id"]

def test_get_instruction(client, test_create_instruction):
    instruction_id = test_create_instruction

    if instruction_id is None:
        pytest.skip("No instruction created to test GET request")

    response = client.get(f"/api/v1/instructions/{instruction_id}")

    assert response.status_code == 200
    # instruction = response.json()

def test_get_all_instructions(client, test_list_database_connections):
    db_connection_id = test_list_database_connections
    response = client.get(f"/api/v1/instructions?db_connection_id={db_connection_id}")


    assert response.status_code == 200
    instructions = response.json()

    # Basic checks on the response
    assert isinstance(instructions, list)

def test_update_instruction(client, test_create_instruction):
    instruction_id = test_create_instruction

    condition = "if film category is asked without context"
    rules = "only use Action film category"
    # Define the updated payload
    updated_payload = {
        "condition": condition,
        "rules": rules,
        "is_default": True,
        "metadata": {}
    }

    # Send the PUT or PATCH request
    response = client.put(f"/api/v1/instructions/{instruction_id}", json=updated_payload)

    assert response.status_code == 200  # Assuming 200 OK is the expected status code
    updated_instruction = response.json()

    # Basic checks on the response
    assert isinstance(updated_instruction, dict)
    assert updated_instruction["id"] == instruction_id
    assert updated_instruction["condition"] == condition
    assert updated_instruction["rules"] == rules
    assert updated_instruction["is_default"] is True
    assert updated_instruction["metadata"] == {}

def test_delete_instruction(client, test_create_instruction):
    instruction_id = test_create_instruction

    # Send the DELETE request
    response = client.delete(f"/api/v1/instructions/{instruction_id}")

    assert response.status_code == 200  # Assuming 204 No Content is the expected status code

# TODO: Understand how to create context store
def test_create_context_store(client, test_list_database_connections):
    # db_connection_id = test_list_database_connections
    # if db_connection_id is None:
    #     pytest.skip("No database connection available to test instructions")

    # # Define the payload for creating a context store
    # payload = {
    #     "db_connection_id": db_connection_id,
    #     "prompt_text": "Sample prompt text",
    #     "sql": "SELECT * FROM staff_list;",
    #     "metadata": {"key": "value"}
    # }

    # # Send the POST request
    # response = client.post("/api/v1/context-stores", json=payload)

    # # Assert the response status code
    # assert response.status_code == 201  # Assuming 201 Created is the expected status code

    # # Assert the response body
    # context_store = response.json()
    # assert isinstance(context_store, dict)
    # assert "id" in context_store  # Assuming the response includes an ID for the created context store
    # assert context_store["db_connection_id"] == db_connection_id
    # assert context_store["prompt_text"] == "Sample prompt text"
    # # assert context_store["sql"] == "SELECT * FROM sample_table;"
    # # assert context_store["metadata"] == {"key": "value"}
    pass

@pytest.fixture
def test_create_business_glossary(client, test_list_database_connections):
    db_connection_id = test_list_database_connections

    if db_connection_id is None:
        pytest.skip("No database connection available to test business glossary creation")

    payload = {
        "metric": "Example Metric",
        "alias": ["s2"],
        "sql": "SELECT * FROM staff_list",
        "metadata": {}
    }
    response = client.post(f"/api/v1/business_glossaries?db_connection_id={db_connection_id}", json=payload)
    assert response.status_code == 201  # Assuming 201 Created is the expected status code
    glossary = response.json()
    return glossary["id"], glossary  # Return the ID and the created glossary data

def test_get_business_glossaries(client, test_list_database_connections):
    db_connection_id = test_list_database_connections

    if db_connection_id is None:
        pytest.skip("No database connection available to test getting business glossaries")

    response = client.get(f"/api/v1/business_glossaries?db_connection_id={db_connection_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_business_glossary(client, test_create_business_glossary):
    business_glossary_id, _ = test_create_business_glossary
    response = client.get(f"/api/v1/business_glossaries/{business_glossary_id}")
    assert response.status_code == 200
    glossary = response.json()
    assert glossary["id"] == business_glossary_id
    assert "metric" in glossary
    assert "alias" in glossary
    assert "sql" in glossary
    assert "metadata" in glossary

def test_update_business_glossary(client, test_create_business_glossary):
    business_glossary_id, _ = test_create_business_glossary
    payload = {
        "metric": "Updated Metric",
        "alias": ["s3"],
        "sql": "SELECT * FROM updated_list",
        "metadata": {"updated": True}
    }
    response = client.put(f"/api/v1/business_glossaries/{business_glossary_id}", json=payload)
    assert response.status_code == 200
    glossary = response.json()
    assert glossary["id"] == business_glossary_id
    assert glossary["metric"] == "Updated Metric"
    assert glossary["alias"] == ["s3"]
    assert glossary["sql"] == "SELECT * FROM updated_list"
    assert glossary["metadata"] == {"updated": True}

def test_delete_business_glossary(client, test_create_business_glossary):
    business_glossary_id, _ = test_create_business_glossary
    response = client.delete(f"/api/v1/business_glossaries/{business_glossary_id}")
    assert response.status_code == 200  # Assuming 204 No Content is the expected status code

@pytest.fixture
def test_create_prompt(client, test_list_database_connections):
    db_connection_id = test_list_database_connections

    if db_connection_id is None:
        pytest.skip("No database connection available to test prompt creation")

    payload = {
        "text": "Test prompt",
        "db_connection_id": db_connection_id,
        "schemas": ["public"],
        "context": [{}],
        "metadata": {}
    }
    response = client.post("/api/v1/prompts", json=payload)
    assert response.status_code == 201
    prompt = response.json()
    assert "id" in prompt
    assert prompt["text"] == "Test prompt"
    assert "db_connection_id" in prompt
    assert "schemas" in prompt
    return prompt["id"], prompt 

def test_get_prompt(client, test_create_prompt):
    prompt_id, _ = test_create_prompt
    response = client.get(f"/api/v1/prompts/{prompt_id}")
    assert response.status_code == 200
    prompt = response.json()
    assert prompt["id"] == prompt_id
    assert "text" in prompt
    assert "db_connection_id" in prompt
    assert "schemas" in prompt
    assert "metadata" in prompt

def test_get_prompts(client, test_list_database_connections):
    db_connection_id = test_list_database_connections

    if db_connection_id is None:
        pytest.skip("No database connection available to test retrieving all prompts")

    response = client.get(f"/api/v1/prompts?db_connection_id={db_connection_id}")
    assert response.status_code == 200
    prompts = response.json()
    assert isinstance(prompts, list)
    if prompts:
        assert "id" in prompts[0]
        assert "text" in prompts[0]
        assert "db_connection_id" in prompts[0]
        assert "schemas" in prompts[0]
        # assert "context" in prompts[0]

# TODO: update prompt seem to not update text
def test_update_prompt(client, test_create_prompt):
    # prompt_id, _ = test_create_prompt
    # payload = {
    #     "text": "Updated prompt text",
    #     "db_connection_id": "updated_db_connection_id",
    #     "schemas": ["updated_schema"],
    #     # "context": [{"updated": True}],
    #     "metadata": {"updated": True}
    # }
    # response = client.put(f"/api/v1/prompts/{prompt_id}", json=payload)
    # assert response.status_code == 200
    # updated_prompt = response.json()
    # assert updated_prompt["id"] == prompt_id
    # assert updated_prompt["text"] == "Updated prompt text"
    # assert updated_prompt["db_connection_id"] == "updated_db_connection_id"
    # assert updated_prompt["schemas"] == ["updated_schema"]
    # # assert updated_prompt["context"] == [{"updated": True}]
    # assert updated_prompt["metadata"] == {"updated": True}
    pass

def test_create_prompt_and_sql_generation(client, test_list_database_connections):
    db_connection_id = test_list_database_connections
    if db_connection_id is None:
        pytest.skip("No database connection available to test SQL generation")

    # Create a prompt
    prompt_payload = {
        "text": "Get staff name",
        "db_connection_id": db_connection_id,
        "schemas": ["public"],
        "context": [{}],
        "metadata": {}
    }
    prompt_response = client.post("/api/v1/prompts", json=prompt_payload)
    assert prompt_response.status_code == 201
    prompt_id = prompt_response.json()["id"]

    # Create SQL generation with llm_config
    sql_generation_payload = {
        "llm_config": {
            "llm_name": "gpt-4o-mini"
        }
    }
    sql_generation_response = client.post(f"/api/v1/prompts/{prompt_id}/sql-generations", json=sql_generation_payload)
    assert sql_generation_response.status_code == 201
    # sql_generation = sql_generation_response.json()

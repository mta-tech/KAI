# API Endpoints List

### Overview

The API provides a range of endpoints for interacting with different services within the KAI platform. Below is a comprehensive list of available endpoints categorized by their functionality.

### Endpoints

#### Database Connections

* **Create Database Connection**
  * **Endpoint:** `POST /api/v1/database-connections`
  * **Description:** Creates a new database connection.
* **List Database Connections**
  * **Endpoint:** `GET /api/v1/database-connections`
  * **Description:** Retrieves a list of all database connections.
* **Update Database Connection**
  * **Endpoint:** `PUT /api/v1/database-connections/{db_connection_id}`
  * **Description:** Updates a specific database connection.

#### Table Descriptions

* **Sync Schemas**
  * **Endpoint:** `POST /api/v1/table-descriptions/sync-schemas`
  * **Description:** Scans and synchronizes database schemas.
* **Refresh Table Description**
  * **Endpoint:** `POST /api/v1/table-descriptions/refresh`
  * **Description:** Refreshes table descriptions for a specified database connection.
* **Update Table Description**
  * **Endpoint:** `PUT /api/v1/table-descriptions/{table_description_id}`
  * **Description:** Updates a specific table description.
* **List Table Descriptions**
  * **Endpoint:** `GET /api/v1/table-descriptions`
  * **Description:** Lists all table descriptions.
* **Get Table Description**
  * **Endpoint:** `GET /api/v1/table-descriptions/{table_description_id}`
  * **Description:** Retrieves detailed information about a specific table description.

#### Instructions

* **Create Instruction**
  * **Endpoint:** `POST /api/v1/instructions`
  * **Description:** Creates a new instruction.
* **Get Instructions**
  * **Endpoint:** `GET /api/v1/instructions`
  * **Description:** Retrieves a list of all instructions.
* **Get Instruction**
  * **Endpoint:** `GET /api/v1/instructions/{instruction_id}`
  * **Description:** Retrieves a specific instruction by its ID.
* **Update Instruction**
  * **Endpoint:** `PUT /api/v1/instructions/{instruction_id}`
  * **Description:** Updates a specific instruction.
* **Delete Instruction**
  * **Endpoint:** `DELETE /api/v1/instructions/{instruction_id}`
  * **Description:** Deletes a specific instruction.

#### Context Stores

* **Create Context Store**
  * **Endpoint:** `POST /api/v1/context-stores`
  * **Description:** Creates a new context store.
* **Get Context Stores**
  * **Endpoint:** `GET /api/v1/context-stores`
  * **Description:** Retrieves a list of all context stores.
* **Get Context Store**
  * **Endpoint:** `GET /api/v1/context-stores/{context_store_id}`
  * **Description:** Retrieves a specific context store by its ID.
* **Delete Context Store**
  * **Endpoint:** `DELETE /api/v1/context-stores/{context_store_id}`
  * **Description:** Deletes a specific context store.

#### Business Glossaries

* **Create Business Glossary**
  * **Endpoint:** `POST /api/v1/business_glossaries`
  * **Description:** Creates a new business glossary.
* **Get Business Glossaries**
  * **Endpoint:** `GET /api/v1/business_glossaries`
  * **Description:** Retrieves a list of all business glossaries.
* **Get Business Glossary**
  * **Endpoint:** `GET /api/v1/business_glossaries/{business_glossary_id}`
  * **Description:** Retrieves a specific business glossary by its ID.
* **Update Business Glossary**
  * **Endpoint:** `PUT /api/v1/business_glossaries/{business_glossary_id}`
  * **Description:** Updates a specific business glossary.
* **Delete Business Glossary**
  * **Endpoint:** `DELETE /api/v1/business_glossaries/{business_glossary_id}`
  * **Description:** Deletes a specific business glossary.

#### Prompts

* **Create Prompt**
  * **Endpoint:** `POST /api/v1/prompts`
  * **Description:** Creates a new prompt.
* **Get Prompt**
  * **Endpoint:** `GET /api/v1/prompts/{prompt_id}`
  * **Description:** Retrieves a specific prompt by its ID.
* **Get Prompts**
  * **Endpoint:** `GET /api/v1/prompts`
  * **Description:** Retrieves a list of all prompts.
* **Update Prompt**
  * **Endpoint:** `PUT /api/v1/prompts/{prompt_id}`
  * **Description:** Updates a specific prompt.

#### SQL Generations

* **Create SQL Generation**
  * **Endpoint:** `POST /api/v1/prompts/{prompt_id}/sql-generations`
  * **Description:** Creates a new SQL generation for a given prompt.
* **Create Prompt and SQL Generation**
  * **Endpoint:** `POST /api/v1/prompts/sql-generations`
  * **Description:** Creates both a prompt and a SQL generation.
* **Get SQL Generations**
  * **Endpoint:** `GET /api/v1/sql-generations`
  * **Description:** Retrieves a list of all SQL generations.
* **Get SQL Generation**
  * **Endpoint:** `GET /api/v1/sql-generations/{sql_generation_id}`
  * **Description:** Retrieves a specific SQL generation by its ID.
* **Update SQL Generation**
  * **Endpoint:** `PUT /api/v1/sql-generations/{sql_generation_id}`
  * **Description:** Updates a specific SQL generation.
* **Execute SQL Query**
  * **Endpoint:** `GET /api/v1/sql-generations/{sql_generation_id}/execute`
  * **Description:** Executes the SQL query of a specific SQL generation.

#### NL Generations

* **Create NL Generation**
  * **Endpoint:** `POST /api/v1/sql-generations/{sql_generation_id}/nl-generations`
  * **Description:** Creates a new NL generation for a given SQL generation.
* **Create SQL and NL Generation**
  * **Endpoint:** `POST /api/v1/prompts/{prompt_id}/sql-generations/nl-generations`
  * **Description:** Creates both SQL and NL generations for a given prompt.
* **Create Prompt, SQL, and NL Generation**
  * **Endpoint:** `POST /api/v1/prompts/sql-generations/nl-generations`
  * **Description:** Creates a prompt, SQL generation, and NL generation all at once.
* **Get NL Generations**
  * **Endpoint:** `GET /api/v1/nl-generations`
  * **Description:** Retrieves a list of all NL generations.
* **Get NL Generation**
  * **Endpoint:** `GET /api/v1/nl-generations/{nl_generation_id}`
  * **Description:** Retrieves a specific NL generation by its ID.
* **Update NL Generation**
  * **Endpoint:** `PUT /api/v1/nl-generations/{nl_generation_id}`
  * **Description:** Updates a specific NL generation.

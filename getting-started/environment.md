---
description: >-
  KAI relies on several environment variables to configure and control its
  behavior. Below is a detailed description of each environment variable used in
  the project:
---

# Environment



```systemd
APP_NAME=KAI API
APP_DESCRIPTION="KAI stands for Knowledge Agent for Intelligence query. This project brings the Gen AI component to be able to embedded into the database so that it can perform analytics and document searches with natural language."
APP_VERSION=1.0.0
APP_ENVIRONMENT=LOCAL

APP_HOST=0.0.0.0
APP_PORT=8000
APP_ENABLE_HOT_RELOAD=0

TYPESENSE_API_KEY = kai_typesense
TYPESENSE_HOST = localhost
TYPESENSE_PORT = 8108
TYPESENSE_PROTOCOL = HTTP
TYPESENSE_TIMEOUT = 2

CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-ada-002"

OPENAI_API_KEY = 
OLLAMA_API_BASE = 
HUGGINGFACEHUB_API_TOKEN = 

# use different tools you can set the "AGENT_MAX_ITERATIONS" env variable. By default it is set to 20 iterations.
AGENT_MAX_ITERATIONS = 20
#timeout in seconds for the engine to return a response. Defaults to 150 seconds
DH_ENGINE_TIMEOUT = 150
#timeout for SQL execution, our agents execute the SQL query to recover from errors, this is the timeout for that execution. Defaults to 60 seconds
SQL_EXECUTION_TIMEOUT = 60
#The upper limit on number of rows returned from the query engine (equivalent to using LIMIT N in PostgreSQL/MySQL/SQlite). Defauls to 50
UPPER_LIMIT_QUERY_RETURN_ROWS = 50
#Encryption key for storing DB connection data in Typesense
ENCRYPT_KEY = f0KVMZHZPgdMStBmVIn2XD049e6Mun7ZEDhf1W7MRnw=
```



### **Server Configuration**

* **`APP_HOST`**\
  _Description:_ The host address on which the application will run.\
  _Example:_ `"0.0.0.0"`
* **`APP_PORT`**\
  _Description:_ The port number on which the application will listen for incoming requests.\
  _Example:_ `"8000"`
* **`APP_ENABLE_HOT_RELOAD`**\
  _Description:_ Enables or disables hot reloading of the application. Set to `1` to enable hot reload, or `0` to disable it.\
  _Example:_ `"0"`

***

### **Typesense Configuration**

* **`TYPESENSE_API_KEY`**\
  _Description:_ The API key used to authenticate requests to the Typesense server.\
  _Example:_ `"kai_typesense"`
* **`TYPESENSE_HOST`**\
  _Description:_ The host address of the Typesense server.\
  _Example:_ `"localhost"`
* **`TYPESENSE_PORT`**\
  _Description:_ The port number on which the Typesense server listens.\
  _Example:_ `"8108"`
* **`TYPESENSE_PROTOCOL`**\
  _Description:_ The protocol used to communicate with the Typesense server.\
  _Example:_ `"HTTP"`
* **`TYPESENSE_TIMEOUT`**\
  _Description:_ The timeout value (in seconds) for requests to the Typesense server.\
  _Example:_ `"2"`

***

### **Model Configuration**

* **`CHAT_MODEL`**\
  _Description:_ The model used for chat and natural language understanding tasks.\
  _Example:_ `"gpt-4o-mini"`
* **`EMBEDDING_MODEL`**\
  _Description:_ The model used for generating embeddings from text data.\
  _Example:_ `"text-embedding-ada-002"`

***

### **API Keys**

* **`OPENAI_API_KEY`**\
  _Description:_ The API key used to authenticate with OpenAI services.\
  _Example:_ `""` _(To be provided)_
* **`OLLAMA_API_BASE`**\
  _Description:_ The base URL for OLLAMA API.\
  _Example:_ `""` _(To be provided)_
* **`HUGGINGFACEHUB_API_TOKEN`**\
  _Description:_ The API token for accessing Hugging Face Hub services.\
  _Example:_ `""` _(To be provided)_

***

### **Agent Configuration**

* **`AGENT_MAX_ITERATIONS`**\
  _Description:_ The maximum number of iterations the agent will perform. This is useful for controlling resource usage.\
  _Example:_ `"20"`
* **`DH_ENGINE_TIMEOUT`**\
  _Description:_ The timeout value (in seconds) for the engine to return a response.\
  _Example:_ `"150"`
* **`SQL_EXECUTION_TIMEOUT`**\
  _Description:_ The timeout (in seconds) for executing SQL queries. This is important for recovering from errors during execution.\
  _Example:_ `"60"`
* **`UPPER_LIMIT_QUERY_RETURN_ROWS`**\
  _Description:_ The upper limit on the number of rows returned from the query engine. This acts similarly to the `LIMIT` clause in SQL.\
  _Example:_ `"50"`
* **`ENCRYPT_KEY`**\
  _Description:_ The encryption key used for securely storing database connection data in Typesense. Use Fernet Generated key for this.\
  _Example:_ `"f0KVMZHZPgdMStBmVIn2XD049e6Mun7ZEDhf1W7MRnw="`

***

These environment variables provide flexibility and control over the behavior of the KAI API, ensuring that the application can be easily configured for different environments and use cases.

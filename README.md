# Getting Started

## **Overview**

KAI, which stands for **Knowledge Agent for Intelligence Query**, is an advanced AI-driven system designed to revolutionize how data is queried, analyzed, and utilized. By embedding a Generative AI component into your database, KAI allows users to perform complex analytics and document searches using natural language queries. This brings a new level of accessibility and efficiency to data interaction, making it easier for both technical and non-technical users to extract valuable insights.

KAI is built to seamlessly integrate with existing databases and systems, enhancing them with powerful AI capabilities. Whether you need to search vast amounts of documents, perform complex data analytics, or interact with your data in a more intuitive way, KAI is equipped to meet those needs.

To access the code, refer to the following [link](https://github.com/mta-tech/KAI).

***

## **Key Features of KAI**

1. **Natural Language Querying**
   * **Description:** KAI enables users to interact with their databases using plain English, eliminating the need for complex SQL queries or other technical languages.
   * **Benefit:** Makes data access and analysis more accessible to non-technical users.
2. **Generative AI Integration**
   * **Description:** Incorporates state-of-the-art Generative AI models to assist with data retrieval, analysis, and content generation.
   * **Benefit:** Enhances the intelligence and flexibility of queries, enabling more accurate and insightful responses.
3. **Real-time Analytics**
   * **Description:** Provides real-time processing and analysis of data, allowing for immediate insights and decision-making.
   * **Benefit:** Supports timely and informed decisions, critical in fast-paced environments.
4. **Document Search and Management**
   * **Description:** KAI includes powerful tools for searching and managing large volumes of documents, making it easy to find relevant information quickly.
   * **Benefit:** Increases productivity by reducing the time spent on manual document searches.
5. **Scalable and Flexible Architecture**
   * **Description:** Designed to be highly scalable, KAI can be deployed across different environments, from local setups to cloud-based infrastructures.
   * **Benefit:** Ensures that KAI can grow with your organization’s needs and integrate with various systems.
6. **Customizable AI Models**
   * **Description:** Allows the use of custom AI models tailored to specific business needs.
   * **Benefit:** Provides flexibility to optimize the AI component for specialized tasks and industries.

***

## Quickstart

Here is a quickstart guide for setting up and running KAI using Docker Compose

### Prerequisites

1. **Docker**: Ensure Docker is installed on your system. You can download it from Docker's official website.
2. **Docker Compose**: Docker Compose is included with Docker Desktop. For standalone installations, you can follow Docker Compose installation instructions.

### Setup

1. Create a .env file using the .env.example file as a reference.&#x20;

```bash
cp .env.example .env
```

2. Make sure to configure these fields for the engine to run.

```
APP_HOST=0.0.0.0
APP_PORT=8000

# OpenAI credentials and model 
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_API_KEY = 

# use different tools you can set the "AGENT_MAX_ITERATIONS" env variable. By default it is set to 20 iterations.
AGENT_MAX_ITERATIONS = 20
#timeout in seconds for the engine to return a response. Defaults to 150 seconds
DH_ENGINE_TIMEOUT = 150
#timeout for SQL execution, our agents execute the SQL query to recover from errors, this is the timeout for that execution. Defaults to 60 seconds
SQL_EXECUTION_TIMEOUT = 60
#The upper limit on number of rows returned from the query engine (equivalent to using LIMIT N in PostgreSQL/MySQL/SQlite). Defauls to 50
UPPER_LIMIT_QUERY_RETURN_ROWS = 50

TYPESENSE_API_KEY = kai_typesense
# Replace TYPESENSE_API_KEY with a secure API key for Typesense if you want.

#Encryption key for storing DB connection data in Typesense
ENCRYPT_KEY = 
```

3. Follow the next commands to generate an ENCRYPT\_KEY and paste it in the .env file like this `ENCRYPT_KEY = 4Mbe2GYx0Hk94o_f-irVHk1fKkCGAt1R7LLw5wHVghI`

<pre data-full-width="false"><code><strong># Install the package cryptography in the terminal
</strong>pip3 install cryptography

# Run python in terminal
python3

# Import Fernet
from cryptography.fernet import Fernet

# Generate the key
Fernet.generate_key()
</code></pre>

### Running the Services

1.  **Navigate to your project directory** where the `docker-compose.yml` file is located:

    ```bash
    cd /path/to/your/project
    ```
2.  **Start the services** using Docker Compose:

    ```bash
    docker compose up -d
    ```

    The `-d` flag runs the containers in detached mode (in the background).
3.  **Verify the containers are running**:

    ```bash
    docker compose ps
    ```

    You should see output indicating that both `typesense` and `kai_engine` services are up and running.

    ```
    NAME         IMAGE                      COMMAND                  SERVICE      CREATED        STATUS          PORTS
    kai_engine   kai-kai_engine             "poetry run python -…"   kai_engine   17 hours ago   Up 20 minutes   0.0.0.0:8000->8000/tcp
    typesense    typesense/typesense:26.0   "/opt/typesense-serv…"   typesense    17 hours ago   Up 20 minutes   0.0.0.0:8108->8108/tcp 
    ```
4. In your browser visit [http://localhost/docs](http://localhost/docs)

#### Stopping the Services

To stop the services, run:

```bash
docker compose down
```

This will stop and remove the containers, but it will retain the data in the `app/data/dbdata` directory for Typesense.

### Additional Notes

* **Network Configuration**: The services are connected via the `kai_network` network, allowing them to communicate.
* **Data Persistence**: The `typesense` container’s data is stored in `./app/data/dbdata` to persist data across container restarts.

With this setup, you should be able to get your product up and running with Docker Compose quickly. Let me know if you have any questions or need further assistance!

***

## Environment

KAI relies on several environment variables to configure and control its behavior. Below is a detailed description of each environment variable used in the project:

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

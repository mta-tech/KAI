---
description: Here is a quickstart guide for setting up and running KAI using Docker Compose
---

# Quickstart

### Quickstart Guide

#### Prerequisites

1. **Docker**: Ensure Docker is installed on your system. You can download it from Docker's official website.
2. **Docker Compose**: Docker Compose is included with Docker Desktop. For standalone installations, you can follow Docker Compose installation instructions.

#### Setup

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

#### Running the Services

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

#### Additional Notes

* **Network Configuration**: The services are connected via the `kai_network` network, allowing them to communicate.
* **Data Persistence**: The `typesense` container’s data is stored in `./app/data/dbdata` to persist data across container restarts.

With this setup, you should be able to get your product up and running with Docker Compose quickly. Let me know if you have any questions or need further assistance!

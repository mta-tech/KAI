# One-Week Onboarding Plan for New Engineers

This onboarding plan is designed to help new engineers get up to speed with the project within their first week. It focuses on a gradual, in-depth understanding of the architecture, codebase, and practical usage.

---

### **Day 1: High-Level Overview & Local Setup**

The goal of Day 1 is to understand the project's purpose and get it running on your local machine.

- [ ] **Project Vision & Capabilities:**
    -   Read the [`README.md`](../README.md). Focus on the "Overview" and "Key Features" sections to understand what KAI does and its main selling points.

- [ ] **System Architecture:**
    -   Review the [`ARCHITECTURE.md`](../ARCHITECTURE.md). Pay close attention to the system architecture diagram to visualize the layers. Read the "Layered Structure" and "Core Components" sections to understand the separation of concerns.

- [ ] **Local Environment Setup:**
    -   Follow the [`GETTING_STARTED.md`](./GETTING_STARTED.md) guide. Use the "Quick Start with Docker" method for the fastest setup.
    -   Ensure you have all the prerequisites listed in the document.
    -   Run `docker compose up -d` and verify that the `kai_engine` and `typesense` containers are running using `docker compose ps`.
    -   Confirm the API is healthy by accessing `http://localhost:8015/health`.

- [ ] **Initial Directory Exploration:**
    -   Familiarize yourself with the high-level directory structure:
        -   `app/`: The core application source code.
        -   `docs/`: All project documentation.
        -   `tests/`: The test suite.
        -   `ui/`: The Next.js web interface.
        -   `.env.example`: The template for environment variables.
        -   `docker-compose.yml`: The Docker service definitions.

---

### **Day 2: Core APIs & Services**

Day 2 focuses on understanding the primary API endpoints and the services that power them.

- [ ] **API Structure Overview:**
    -   Study [`docs/apis/README.md`](./apis/README.md) for an introduction to the API documentation structure and conventions.

- [ ] **Hands-on API Interaction with Postman:**
    -   Import the Postman collection from `docs/postman/KAI_LangGraph_API.postman_collection.json`.
    -   Practice making requests to your local instance for the following core services:
        -   **Database Connections:** Use the `Create Database Connection` and `List Database Connections` requests.
        -   **Prompts & SQL Generations:** Use the `Create Prompt and SQL Generation` request to see the basic NL-to-SQL functionality.

- [ ] **Service Layer Deep Dive:**
    -   Read through the service documentation in [`docs/services/`](./services/) to connect API endpoints to their underlying business logic. Start with `database-connection-services.md` and `sql-generation-services.md`.

- [ ] **Trace a Request from API to Service:**
    -   Choose a simple API endpoint, like `POST /api/v1/database-connections`.
    -   Find its implementation in `app/api/__init__.py`.
    -   Trace the call to the `self.db_connection_service.create_database_connection` method.
    -   Follow the logic into `app/modules/database_connection/services/__init__.py` to see how the business logic is executed.

---

### **Day 3: Deep Dive into the Codebase**

The goal of Day 3 is to understand how the application is structured and how data flows through it.

- [ ] **Application Entrypoint & Configuration:**
    -   Examine `app/main.py`. Note how the FastAPI app is created and how the main API router from `app/api/__init__.py` is included.

- [ ] **Modular Design in Practice:**
    -   Explore the `app/modules/` directory. Select the `database_connection` module (`app/modules/database_connection/`).
    -   Study its internal structure:
        -   `models/`: Look at the Pydantic models that define the data structures.
        -   `repositories/`: Examine the repository class to see how it interacts with the storage layer.
        -   `services/`: Read the service class to understand the business logic.

- [ ] **Data Modeling & Schemas:**
    -   Review the database schemas in `app/data/db/schemas/`. Look at `database_connections.json` and `table_descriptions.json` to understand how the core data is structured in Typesense.

- [ ] **Database Interaction Layer:**
    -   Open `app/data/db/storage.py`. Study the `Storage` class and its methods (`create`, `get`, `search`, etc.) to see how the application provides a unified interface for interacting with Typesense.

---

### **Day 4: Advanced Concepts & Practical Tutorial**

Day 4 introduces more advanced features and provides a hands-on, end-to-end tutorial.

- [ ] **Complete the End-to-End Tutorial:**
    -   Follow the [`koperasi-analysis-tutorial.md`](./tutorials/koperasi-analysis-tutorial.md) from start to finish.
    -   This includes setting up the sample PostgreSQL database using the provided `setup_database.sql` script in `docs/tutorials/koperasi-sample-data/`.

- [ ] **Understanding the Semantic Layer:**
    -   Read [`mdl-semantic-layer.md`](./tutorials/mdl-semantic-layer.md) to understand how the project uses a semantic layer for business intelligence and how it connects to the core services.

- [ ] **Introduction to the Agentic Core:**
    -   Explore `app/langgraph_server/graphs.py`. This file defines the core conversational agent logic using LangGraph.
    -   Look at the `app/agents/` directory to see how different agentic capabilities are structured.

---

### **Day 5: Hands-on Task & Debugging**

Day 5 is about applying your knowledge with a practical coding task and learning how to debug the application.

- [ ] **Familiarize with Troubleshooting:**
    -   Read [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) to learn about common issues and their solutions.

- [ ] **Practical Task: Add a Health Check Endpoint:**
    -   Open `app/main.py`.
    -   Add a new `GET /health` endpoint using the `@app.get("/health")` decorator.
    -   The endpoint function should return a simple JSON response: `return {"status": "ok"}`.
    -   Run the application and verify that your new endpoint works correctly by accessing `http://localhost:8015/health` in your browser or with `curl`.

- [ ] **Debugging Practice:**
    -   If you are using VS Code, create a `launch.json` file in the `.vscode` directory with a Python debug configuration for FastAPI.
    -   Set breakpoints in a service function, for example, inside the `create_database_connection` method in `app/modules/database_connection/services/__init__.py`.
    -   Run the application in debug mode.
    -   Make an API request to the corresponding endpoint using Postman.
    -   Step through the code line by line to understand the runtime execution flow.
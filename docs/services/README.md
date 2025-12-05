# Services

This directory contains documentation for the service layer components of KAI. Services encapsulate business logic and coordinate between repositories, external APIs, and other system components.

## Available Services

| Service | Description |
|---------|-------------|
| [Business Glossary Services](./business-glossary-services.md) | Manages business metrics and glossary definitions |
| [Database Connection Services](./database-connection-services.md) | Handles database connections and schema management |
| [Instruction Services](./instruction-services.md) | Manages instructions for SQL generation guidance |
| [NL Generation Services](./nl-generation-services.md) | Converts SQL results to natural language responses |
| [Prompt Services](./prompt-services.md) | Manages user prompts and query history |
| [RAG Services](./rag-services.md) | Document storage and knowledge retrieval with embeddings |
| [SQL Generation Services](./sql-generation-services.md) | Generates SQL queries from natural language prompts |
| [Table Description Service](./table-description-service.md) | Manages database schema metadata and descriptions |

## Service Architecture

Services in KAI follow a layered architecture:

1. **API Layer** - Handles HTTP requests and responses
2. **Service Layer** - Contains business logic (documented here)
3. **Repository Layer** - Manages data persistence
4. **Model Layer** - Defines data structures

Each service typically:
- Receives requests from the API layer
- Validates input data
- Coordinates with repositories for data access
- Integrates with external services (LLMs, vector stores)
- Returns structured responses

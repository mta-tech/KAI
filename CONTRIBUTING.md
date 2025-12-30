# Contributing to KAI

Thank you for your interest in contributing to KAI! We're excited to have you as part of our community. Whether you're fixing bugs, adding features, improving documentation, or helping others, your contributions are valuable.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git
- uv package manager

### Initial Setup

1. **Fork the repository**

   Click the "Fork" button on GitHub to create your own copy.

2. **Clone your fork**

   ```bash
   git clone https://github.com/your-username/kai.git
   cd kai
   ```

3. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/original-org/kai.git
   ```

4. **Install dependencies**

   ```bash
   uv sync
   ```

5. **Set up environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Start Typesense**

   ```bash
   docker compose up typesense -d
   ```

7. **Run the development server**

   ```bash
   uv run python -m app.main
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
# or
git checkout -b docs/documentation-update
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### 2. Make Your Changes

- Write clear, concise code
- Follow existing code patterns
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific tests
uv run pytest tests/modules/session/
```

### 4. Commit Your Changes

Write clear, meaningful commit messages:

```bash
git add .
git commit -m "feat: add natural language dashboard generation"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 6. Push Your Changes

```bash
git push origin feature/your-feature-name
```

## Pull Request Process

### Creating a Pull Request

1. **Navigate to GitHub**

   Go to your fork on GitHub and click "Compare & pull request"

2. **Fill in PR details**

   - **Title**: Clear, descriptive title (e.g., "Add forecasting support for time series data")
   - **Description**: Include:
     - What changes were made
     - Why they were made
     - How to test them
     - Related issues (e.g., "Closes #123")

3. **Submit for review**

   Submit the PR and be responsive to feedback

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing
- [ ] All tests pass
- [ ] Added new tests for new functionality
- [ ] Tested manually

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages are clear
```

### Review Process

- A maintainer will review your PR
- Address any feedback or requested changes
- Once approved, a maintainer will merge your PR

## Code Style Guidelines

### Python Code Style

We use **ruff** for linting and **black** for formatting:

```bash
# Format code
uv run black app/ tests/

# Lint code
uv run ruff check app/ tests/

# Fix auto-fixable issues
uv run ruff check --fix app/ tests/
```

### Style Principles

1. **Follow PEP 8** conventions
2. **Use type hints** for all function parameters and return values
3. **Write docstrings** for classes and complex functions
4. **Keep functions focused** - one responsibility per function
5. **Use async/await** for I/O operations
6. **Avoid deep nesting** - extract complex logic into helper functions

### Example Code

```python
from typing import Optional
from pydantic import BaseModel

class DatabaseConnection(BaseModel):
    """Database connection configuration.

    Attributes:
        uri: Database connection URI
        alias: Human-readable connection name
        description: Optional connection description
    """
    uri: str
    alias: str
    description: Optional[str] = None

async def create_connection(
    connection: DatabaseConnection,
    storage: Storage,
) -> str:
    """Create a new database connection.

    Args:
        connection: Database connection configuration
        storage: Storage backend for persisting connection

    Returns:
        The connection ID

    Raises:
        ValueError: If connection with alias already exists
    """
    existing = await storage.find_by_alias(connection.alias)
    if existing:
        raise ValueError(f"Connection '{connection.alias}' already exists")

    return await storage.create(connection)
```

## Testing Guidelines

### Test Structure

- Place tests in `tests/` directory mirroring `app/` structure
- Name test files with `test_` prefix
- Use descriptive test function names

### Writing Tests

```python
import pytest
from app.modules.session.services import SessionService

@pytest.mark.asyncio
async def test_create_session_success():
    """Test successful session creation."""
    service = SessionService(storage=mock_storage)

    session = await service.create_session(
        db_alias="test_db",
        user_id="user123"
    )

    assert session.id is not None
    assert session.db_alias == "test_db"
    assert session.status == "active"

@pytest.mark.asyncio
async def test_create_session_invalid_db():
    """Test session creation with non-existent database."""
    service = SessionService(storage=mock_storage)

    with pytest.raises(ValueError, match="Database not found"):
        await service.create_session(
            db_alias="nonexistent",
            user_id="user123"
        )
```

### Test Coverage

- Aim for **>80% code coverage**
- Test both success and failure cases
- Include edge cases and error handling
- Test async code properly with `@pytest.mark.asyncio`

## Documentation

### Documentation Standards

1. **Code Comments**
   - Explain *why*, not *what*
   - Keep comments up-to-date with code changes

2. **Docstrings**
   - Use Google-style docstrings
   - Document all public functions and classes
   - Include usage examples for complex functions

3. **API Documentation**
   - Update OpenAPI schema if adding/changing endpoints
   - Include request/response examples

4. **README Updates**
   - Add new features to feature list
   - Update installation/setup if needed

### Documentation Locations

- **API docs**: `docs/apis/`
- **Tutorials**: `docs/tutorials/`
- **Architecture**: `ARCHITECTURE.md`
- **Deployment**: `docs/DEPLOYMENT.md`

## Community

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Check existing docs first

### Ways to Contribute

Not a coder? You can still contribute!

- **Documentation**: Improve guides and tutorials
- **Bug Reports**: Report issues with clear reproduction steps
- **Feature Requests**: Suggest new features or improvements
- **Design**: UI/UX improvements
- **Translation**: Help translate documentation
- **Community Support**: Help others in discussions

### Recognition

All contributors are recognized in our:
- GitHub contributors page
- Release notes
- Project documentation

Thank you for contributing to KAI!

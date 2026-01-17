# Deals Processor API

A modern, production-ready FastAPI application for processing deals with clean architecture and SOLID principles.

## Features

- **Clean Architecture** — Separation of concerns with clear layers (API, Services, Models, Core)
- **SOLID Principles** — Following Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion
- **Type Safety** — Full Python type hints with mypy strict mode
- **Code Quality** — Automated linting with ruff, formatting with black
- **Testing** — Comprehensive unit tests with pytest and coverage reporting
- **Dependency Management** — Using `uv` for fast, reliable dependency management
- **Configuration Management** — Environment-based settings with pydantic-settings
- **Structured Logging** — Built-in application logging with configurable levels
- **API Documentation** — Auto-generated OpenAPI/Swagger documentation

## Project Structure

```
deals_processor/
├── src/deals_processor/          # Source code
│   ├── api/                      # API routes and endpoints
│   │   ├── health.py             # Health check endpoints
│   │   └── deals.py              # Deal management endpoints
│   ├── core/                     # Core application logic
│   │   ├── config.py             # Configuration management
│   │   ├── container.py          # Dependency injection container
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── __init__.py
│   ├── models/                   # Domain models
│   │   └── __init__.py           # Deal domain model
│   ├── schemas/                  # Pydantic schemas (DTOs)
│   │   └── __init__.py           # Deal schemas
│   ├── services/                 # Business logic services
│   │   └── __init__.py           # Deal service
│   ├── main.py                   # Application factory
│   └── __init__.py
├── tests/                        # Test suite
│   ├── conftest.py               # Pytest configuration and fixtures
│   ├── unit/                     # Unit tests
│   │   ├── test_health.py
│   │   ├── test_services.py
│   │   └── test_deals_api.py
│   └── integration/              # Integration tests
├── pyproject.toml                # Project configuration
├── .editorconfig                 # Editor configuration
├── constraints.txt               # Dependency constraints
├── README.md                     # This file
└── .env.example                  # Environment variables template
```

## Quick Start

### Prerequisites

- Python 3.10 or higher

### Installation

1. **Navigate to the project**

   ```bash
   cd MyProjects/deals_processor
   ```

2. **Create virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

### Running the Application

**Using the entry point (recommended):**

```bash
# Activate the virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate
run-deals-processor
```

### User Details
The application comes with pre-defined users for testing:
| Username             | Password   | Role    |
|----------------------|------------|---------|
| admin@default.com    | admin123   | admin   |
| testuser@example.com | test123456 | analyst |
| user1@example.com    | user123456 | partner |


The API will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`


## Development

### Code Quality Tools

#### Linting with Ruff

Check code style:
```bash
ruff check src/ tests/
```

Auto-fix issues:
```bash
ruff check --fix src/ tests/
```

#### Type Checking with MyPy

Run type checker:
```bash
mypy src/
```

#### Code Formatting with Black

Format code:
```bash
black src/ tests/
```

Check formatting:
```bash
black --check src/ tests/
```

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src/deals_processor
```

Run specific test file:
```bash
pytest tests/unit/test_deals_api.py -v
```

Run only unit tests:
```bash
pytest -m unit
```

### Using Make Commands

Convenient make commands:

```bash
make run              # Start development server
make run-prod         # Production mode
make test             # Run tests
make test-cov         # Tests with coverage
make lint             # Check code
make lint-fix         # Auto-fix linting
make format           # Format code
make type-check       # Type checking
make check-all        # All checks at once
make clean            # Clean artifacts
```

### Pre-commit Hooks (Optional)

To automatically run checks before committing:

```bash
pre-commit install
```

## API Endpoints

### Health Check

- **GET** `/api/v1/health` — Check application health status

### Deals Management

- **GET** `/api/v1/deals` — List all deals (supports `?status=active` filter)
- **POST** `/api/v1/deals` — Create a new deal
- **GET** `/api/v1/deals/{deal_id}` — Get a specific deal
- **PUT** `/api/v1/deals/{deal_id}` — Update a deal
- **DELETE** `/api/v1/deals/{deal_id}` — Delete a deal
- **GET** `/api/v1/deals/stats/active-count` — Get count of active deals

### Request/Response Examples

**Create a Deal:**
```bash
curl -X POST "http://localhost:8000/api/v1/deals" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Enterprise License",
    "description": "Annual enterprise license agreement",
    "amount": 50000.0,
    "status": "pending"
  }'
```

**List Deals:**
```bash
curl "http://localhost:8000/api/v1/deals?status=active"
```

**Update a Deal:**
```bash
curl -X PUT "http://localhost:8000/api/v1/deals/{deal_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "amount": 55000.0
  }'
```

## Architecture & Design Patterns

### Clean Architecture

The project follows clean architecture principles with distinct layers:

1. **Presentation Layer** (`api/`) — HTTP requests/responses
2. **Business Logic Layer** (`services/`) — Core application logic
3. **Domain Layer** (`models/`) — Business entities
4. **Infrastructure Layer** (`core/`) — Configuration, DI, exceptions

### SOLID Principles

- **S**ingle Responsibility — Each class has one reason to change
- **O**pen/Closed — Open for extension, closed for modification
- **L**iskov Substitution — Derived classes can substitute base classes
- **I**nterface Segregation — Many client-specific interfaces
- **D**ependency Inversion — Depend on abstractions, not concretions

### Design Patterns Used

- **Dependency Injection** — Services injected via FastAPI's `Depends()`
- **Service Layer** — Business logic encapsulation
- **Repository Pattern** — Data access abstraction (ready for database integration)
- **Factory Pattern** — Application factory in `main.py`
- **Data Transfer Object** — Pydantic schemas for validation

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
APP_NAME=Deals Processor API
APP_VERSION=0.1.0
DEBUG=False
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

Settings are loaded automatically from environment variables and the `.env` file.

### Customization

Edit `src/deals_processor/core/config.py` to add new configuration options:

```python
class Settings(BaseSettings):
    your_new_setting: str = "default_value"
```

## Extending the Application

### Adding New Endpoints

1. Create a new file in `src/deals_processor/api/`
2. Define routes using FastAPI router:

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/items", tags=["items"])

@router.get("")
async def list_items() -> list[str]:
    """List all items."""
    return []
```

3. Include router in `main.py`:

```python
from deals_processor.api import your_module

def include_routers(app: FastAPI) -> None:
    app.include_router(your_module.router)
```

### Adding New Services

1. Create a new service class in `src/deals_processor/services/`
2. Implement business logic
3. Inject into routes via `Depends()`

### Database Integration

To add database support:

1. Add ORM (SQLAlchemy, Tortoise-ORM) to dependencies
2. Create models in `models/` directory
3. Create repository layer for data access
4. Inject repositories into services

## Testing Strategy

The project uses pytest with the following organization:

- **Unit Tests** — Test individual components (services, models)
- **Integration Tests** — Test component interactions
- **Fixtures** — Reusable test data and setup in `conftest.py`

Run tests with markers:
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

## Performance & Optimization

- **Async Support** — FastAPI uses async by default
- **Dependency Caching** — Settings cached with `@lru_cache`
- **Type Hints** — Enable better IDE support and potential optimization

## Security Considerations

For production deployment:

1. **Authentication** — Add JWT or OAuth2 in `core/`
2. **Rate Limiting** — Use FastAPI middleware or external service
3. **CORS** — Configure allowed origins
4. **Input Validation** — Already implemented with Pydantic
5. **Environment Secrets** — Use `.env` for sensitive data (never commit)

## Troubleshooting

### ModuleNotFoundError

Ensure you're using the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Type Checking Errors

Run mypy to identify issues:
```bash
uv run mypy src/ --show-error-codes
```

### Test Failures

Check test output with verbose flag:
```bash
uv run pytest -vv
```

## Contributing

1. Follow SOLID principles and clean architecture
2. Add type hints to all functions
3. Write docstrings following Google style
4. Add tests for new features
5. Run quality checks before committing:

```bash
uv run ruff check --fix .
uv run black .
uv run mypy src/
uv run pytest
```

## License

MIT License

## Support

For issues or questions, refer to the FastAPI documentation: https://fastapi.tiangolo.com/

---

**Happy coding! 🚀**

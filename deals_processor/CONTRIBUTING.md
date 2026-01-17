# Contributing to Deals Processor

This guide explains how to maintain code quality and contribute to the Deals Processor API.

## Code Quality Standards

### Type Hints (Required)

All functions must have complete type hints:

```python
# ✓ Good
def create_deal(
    title: str,
    amount: float,
    description: str | None = None,
) -> Deal:
    """Create a new deal."""
    ...

# ✗ Bad - missing return type
def create_deal(title, amount, description=None):
    ...
```

### Docstrings (Required)

All public classes and functions must have Google-style docstrings:

```python
def create_deal(
    title: str,
    amount: float,
) -> Deal:
    """Create a new deal.

    Args:
        title: Deal title, must be non-empty.
        amount: Deal amount, must be positive.

    Returns:
        Deal: Created deal instance.

    Raises:
        ValidationError: If validation fails.
    """
    ...
```

### Line Length

Maximum line length is 100 characters. This is enforced by ruff and black.

```python
# ✓ Good - fits within 100 chars
def process_deal(deal_id: str) -> None:
    """Process a deal."""
    ...

# If exceeding, break into multiple lines
def create_complex_deal(
    title: str,
    description: str,
    amount: float,
    status: DealStatus,
) -> Deal:
    """Create a deal with complex parameters."""
    ...
```

### Naming Conventions

Follow PEP 8 naming conventions:

```python
# Classes: PascalCase
class DealService: ...

# Functions/variables: snake_case
def get_active_deals() -> list[Deal]: ...
active_deals: list[Deal] = []

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# Private: leading underscore
class Container:
    def _init_dependencies(self) -> None: ...
```

## Pre-Commit Checks

Run these checks before committing:

### Linting with Ruff

```bash
make lint-fix  # Auto-fix issues
# or manually
uv run ruff check --fix src/ tests/
```

Ruff checks for:
- Style violations (PEP 8)
- Logical errors
- Import sorting
- Docstring issues
- Naming conventions

### Formatting with Black

```bash
make format
# or manually
uv run black src/ tests/
```

Black ensures consistent code formatting.

### Type Checking with MyPy

```bash
make type-check
# or manually
uv run mypy src/
```

MyPy performs static type checking in strict mode.

### Running Tests

```bash
make test
# or manually
uv run pytest
```

## Commit Workflow

1. **Make changes** to source files

2. **Run checks**
   ```bash
   make check-all
   ```

3. **Run tests** with coverage
   ```bash
   make test-cov
   ```

4. **Fix any issues** reported by tools

5. **Commit** when all checks pass
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

## Git Commit Messages

Follow conventional commits format:

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat:` — A new feature
- `fix:` — A bug fix
- `docs:` — Documentation changes
- `refactor:` — Code refactoring without feature changes
- `test:` — Test additions or modifications
- `chore:` — Dependency updates, configuration changes
- `perf:` — Performance improvements

### Examples

```
feat: add customer management endpoints

- Create customer CRUD routes
- Implement CustomerService
- Add customer domain model
- Add tests for customer endpoints

Closes #123
```

```
fix: handle negative amounts in deal update

ValidationError now raised when attempting to set
negative amount on deal update operation.
```

```
docs: update API endpoint documentation
```

## Testing Guidelines

### Unit Tests

Test individual components:

```python
@pytest.mark.unit
def test_create_deal(service):
    """Test creating a valid deal."""
    deal = service.create_deal("Test", 100.0)
    assert deal.title == "Test"
    assert deal.status == DealStatus.PENDING
```

### Test Coverage

Maintain test coverage above 80%:

```bash
make test-cov
```

View HTML coverage report:
```bash
open htmlcov/index.html
```

### Test Organization

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Fixtures in `tests/conftest.py`
- Name files as `test_<module>.py`

### Example Test Structure

```python
@pytest.mark.unit
def test_function_name_describes_behavior(fixture):
    """Test docstring explains what is being tested.

    Args:
        fixture: Description of fixture.
    """
    # Arrange
    input_data = {...}

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result.property == expected_value
```

## Code Review Checklist

When submitting or reviewing code:

- [ ] Type hints on all functions
- [ ] Docstrings on public functions/classes
- [ ] Follows naming conventions
- [ ] Tests added for new features
- [ ] Tests pass: `make test`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] No unnecessary imports
- [ ] No hardcoded values (use config)
- [ ] Follows SOLID principles
- [ ] Error handling with custom exceptions

## Common Issues

### Type Checking Fails

Check error messages:
```bash
uv run mypy src/ --show-error-codes
```

Common fixes:
- Add missing type hints: `def func(x: int) -> str:`
- Use `| None` for optional types
- Import types from `typing` module

### Ruff Linting Issues

Auto-fix most issues:
```bash
uv run ruff check --fix src/
```

For unused imports:
```python
# Remove these imports
import unused_module  # ✗ Remove
import os  # ✓ Keep if used
```

### Test Failures

Run with verbose output:
```bash
uv run pytest -vv tests/unit/test_file.py::test_function
```

Check test setup in `conftest.py` if fixtures are involved.

## Adding Dependencies

1. **Edit `pyproject.toml`**
   ```toml
   dependencies = [
       ...,
       "new-package>=1.0.0",
   ]
   ```

2. **Update constraints.txt**
   ```
   new-package>=1.0.0
   ```

3. **Sync environment**
   ```bash
   uv sync
   ```

4. **Test everything still works**
   ```bash
   make test
   ```

## Documentation Updates

When making changes:

1. Update docstrings if behavior changes
2. Update README.md for new features
3. Update ARCHITECTURE.md if design changes
4. Add examples for new endpoints

## Questions or Issues?

- Review ARCHITECTURE.md for design patterns
- Check README.md for setup and API documentation
- Look at existing code for examples
- Refer to FastAPI documentation: https://fastapi.tiangolo.com/

---

**Thank you for contributing!** 🎉

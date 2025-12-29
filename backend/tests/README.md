# Backend Testing with pytest and Polyfactory

This document explains how to run tests for the Sneaker Engine backend.

## Setup

The test environment has been configured with:
- **pytest** 8.3.4 - Testing framework
- **pytest-asyncio** 0.24.0 - Async test support
- **polyfactory** 2.17.0 - Test data generation
- **httpx** 0.28.1 - HTTP client for API testing

## Running Tests

### Run All Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Run Specific Test Files
```bash
# Run factory tests only
python -m pytest tests/test_factories.py -v

# Run auth tests only
python -m pytest tests/test_auth.py -v

# Run sneaker endpoint tests only
python -m pytest tests/test_sneakers.py -v
```

### Run with Coverage
```bash
# Install coverage first
pip install pytest-cov

# Run tests with coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### Run Specific Tests by Marker
```bash
# Run only unit tests
python -m pytest tests/ -m unit -v

# Run only integration tests
python -m pytest tests/ -m integration -v

# Skip slow tests
python -m pytest tests/ -m "not slow" -v
```

## Test Structure

```
backend/tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── factories/               # Polyfactory test data factories
│   ├── __init__.py
│   ├── base.py             # Base factory configuration
│   ├── user_factory.py     # User model factory
│   └── sneaker_factory.py  # Sneaker model factory
├── test_auth.py            # Authentication endpoint tests
├── test_factories.py       # Factory functionality tests
└── test_sneakers.py        # Sneaker endpoint tests
```

## Using Polyfactory Factories

### Generate Test Data

```python
from tests.factories.user_factory import UserFactory
from tests.factories.sneaker_factory import SneakerFactory

# Build a single user (not persisted to DB)
user = UserFactory.build()

# Build with custom values
user = UserFactory.build(email="custom@example.com")

# Build multiple users
users = UserFactory.batch(5)

# Persist to database (requires session fixture)
user = UserFactory.create_sync(session=db_session)
```

### Factory Features

- **Automatic data generation** - Uses Faker for realistic data
- **Custom field values** - Override any field during generation
- **Batch generation** - Create multiple instances at once
- **Relationship handling** - Automatically handles foreign keys
- **Type safety** - Uses Python type hints

## Shared Fixtures

Located in [conftest.py](conftest.py):

- `db_engine` - Fresh in-memory SQLite database engine
- `db_session` - Database session for tests
- `client` - FastAPI TestClient with DB override
- `test_password` - Standard test password
- `hashed_test_password` - Hashed version of test password
- `auth_headers` - Authentication headers for authenticated endpoints

### Example Usage

```python
def test_create_user(db_session: Session, client: TestClient):
    \"\"\"Test creating a new user.\"\"\"
    user = UserFactory.build()
    db_session.add(user)
    db_session.commit()
    
    # Test API endpoint
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 200
```

## Test Configuration

Configuration is in [pyproject.toml](../pyproject.toml):

```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib", "-v", "--tb=short", "--strict-markers"]
testpaths = ["tests"]
pythonpath = ["."]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "auth: marks tests related to authentication",
]
asyncio_mode = "auto"
```

## Writing New Tests

### 1. Create Test File

File must be named `test_*.py` or `*_test.py`:

```python
# tests/test_new_feature.py
import pytest
from tests.factories.user_factory import UserFactory

class TestNewFeature:
    \"\"\"Test suite for new feature.\"\"\"
    
    def test_something(self, db_session):
        \"\"\"Test description.\"\"\"
        user = UserFactory.build()
        assert user.email is not None
```

### 2. Add Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_user_validation():
    \"\"\"Unit test for user validation.\"\"\"
    pass

@pytest.mark.integration
def test_user_creation_flow(client, db_session):
    \"\"\"Integration test for user creation.\"\"\"
    pass

@pytest.mark.slow
def test_bulk_operations():
    \"\"\"Slow test for bulk operations.\"\"\"
    pass
```

### 3. Use Fixtures

Leverage shared fixtures for common setup:

```python
def test_authenticated_request(client, auth_headers):
    \"\"\"Test requires authentication.\"\"\"
    response = client.get("/api/protected", headers=auth_headers)
    assert response.status_code == 200
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run all tests with strict mode
python -m pytest tests/ --strict-markers -v

# Generate coverage report
python -m pytest tests/ --cov=. --cov-report=xml --cov-report=term

# Fail if coverage below threshold
python -m pytest tests/ --cov=. --cov-fail-under=80
```

## Troubleshooting

### Import Errors

Make sure you're in the backend directory and using the virtual environment:

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

python -m pytest tests/
```

### Database Errors

Tests use in-memory SQLite by default. If you see database errors:
1. Check that models are properly imported in conftest.py
2. Verify foreign key relationships are set correctly
3. Ensure fixtures are creating tables before tests

### Factory Errors

If factory generation fails:
1. Check that the model class is correctly referenced
2. Verify all required fields have defaults or Use() providers
3. Check for circular dependencies in relationships

## Next Steps

1. **Add more test coverage** - Aim for >80% code coverage
2. **Add integration tests** - Test full API workflows
3. **Add performance tests** - Test with larger datasets
4. **Add E2E tests** - Test complete user journeys

## References

- [pytest documentation](https://docs.pytest.org/)
- [Polyfactory documentation](https://polyfactory.litestar.dev/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Backend Test Instructions](./copilot-backend-test-instructions.md)
- [Backend Polyfactory Instructions](./copilot-backend-polyfactory-instructions.md)

# GitHub Copilot Instructions for Backend Testing with pytest

**IMPORTANT**: When writing tests for this backend, always refer to these pytest best practices.

## Project Context
- **Framework**: FastAPI backend with PostgreSQL database
- **ORM**: SQLAlchemy
- **Auth**: JWT token-based authentication
- **Test Framework**: pytest
- **Test Data Generation**: Polyfactory (see [copilot-backend-polyfactory-instructions.md](./copilot-backend-polyfactory-instructions.md))

## Documentation References
- pytest documentation: https://docs.pytest.org/en/stable/
- Polyfactory documentation: https://polyfactory.litestar.dev/latest/
- **See also**: [copilot-backend-polyfactory-instructions.md](./copilot-backend-polyfactory-instructions.md) for detailed Polyfactory usage

## CRITICAL: Keep Factories in Sync with Models

**⚠️ ALWAYS update test factories when you modify SQLAlchemy models!**

When you change a model in `models/`, you MUST update the corresponding factory in `tests/factories/`:

### When Adding a Field to a Model
```python
# models/user.py - Added 'phone_number' field
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20))  # NEW FIELD
```

**YOU MUST update the factory:**
```python
# tests/factories/user_factory.py
from polyfactory import Use

class UserFactory(BaseFactory):
    __model__ = User
    
    email = Use(lambda: UserFactory.__faker__.email())
    phone_number = Use(lambda: UserFactory.__faker__.phone_number())  # ADD THIS
```

### When Removing a Field from a Model
```python
# models/user.py - Removed 'middle_name' field
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    # middle_name removed
```

**YOU MUST update the factory:**
```python
# tests/factories/user_factory.py
class UserFactory(BaseFactory):
    __model__ = User
    
    email = Use(lambda: UserFactory.__faker__.email())
    # REMOVE middle_name = Use(...)
```

### When Changing Field Constraints
```python
# models/user.py - Changed email to unique and required
class User(Base):
    __tablename__ = "users"
    email = Column(String(255), unique=True, nullable=False)  # CHANGED
```

**Ensure factory generates unique values:**
```python
# tests/factories/user_factory.py
class UserFactory(BaseFactory):
    __model__ = User
    
    # Faker automatically generates unique emails in most cases,
    # but you can add custom logic if needed
    email = Use(lambda: UserFactory.__faker__.unique.email())
```

### When Adding Relationships
```python
# models/sneaker.py - Added relationship to User
class Sneaker(Base):
    __tablename__ = "sneakers"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="sneakers")  # NEW
```

**Update factory to handle foreign keys:**
```python
# tests/factories/sneaker_factory.py
class SneakerFactory(BaseFactory):
    __model__ = Sneaker
    
    # Ensure user_id is provided when building
    # Tests should pass user_id explicitly:
    # sneaker = SneakerFactory.build(user_id=user.id)
```

### Checklist for Model Changes

- [ ] Updated model in `models/`
- [ ] Updated corresponding factory in `tests/factories/`
- [ ] Ran all tests to ensure factories work: `pytest tests/test_factories.py -v`
- [ ] Updated any affected test files
- [ ] Ran full test suite: `pytest tests/ -v`

### Why This Matters

1. **Tests will fail** if factories don't match models
2. **False positives** if factories generate invalid data
3. **Debugging nightmare** when tests use outdated factories
4. **CI/CD failures** that could have been caught early

**Make it a habit**: Every time you touch `models/`, check `tests/factories/`!

## Test Discovery & Structure

### Project Layout
Use the **"tests outside application code"** layout (recommended by pytest):

```
backend/
├── alembic/
├── crud/
├── models/
├── routes/
├── schemas/
├── auth.py
├── database.py
├── main.py
└── tests/              # Test directory separate from app code
    ├── conftest.py     # Shared fixtures and configuration
    ├── factories/      # Polyfactory test data factories
    │   ├── __init__.py
    │   ├── base.py
    │   ├── user_factory.py
    │   └── sneaker_factory.py
    ├── test_auth.py
    ├── test_users.py
    └── test_sneakers.py
```

**Benefits**:
- Tests run against installed version after `pip install -e .`
- Clear separation between test and application code
- Easier to exclude tests from distribution packages

### Test Discovery Conventions
pytest automatically discovers tests following these rules:

1. **File naming**: `test_*.py` or `*_test.py`
2. **Function naming**: `test_*` prefix (e.g., `test_create_user()`)
3. **Class naming**: `Test*` prefix (e.g., `class TestUserAPI:`)
   - Test classes should **NOT** have an `__init__` method
   - Methods inside test classes must have `test_*` prefix
4. **Directory structure**: Recurses into subdirectories unless excluded in config

### Import Mode Configuration
For new projects, use **`importlib`** import mode in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
testpaths = ["tests"]
pythonpath = ["."]
```

**Why `importlib`?**
- Doesn't modify `sys.path` (less surprising behavior)
- No need for unique test file names across directories
- Cleaner imports and better package isolation

## Configuration & Setup

### pytest Configuration File
Use `pyproject.toml` (modern) or `pytest.ini` (legacy):

```toml
[tool.pytest.ini_options]
# Import mode
addopts = ["--import-mode=importlib"]

# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Output
addopts = ["-v", "--tb=short"]

# Strict mode (recommended for new projects)
strict = true

# Markers (define custom markers here)
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Strict Mode
Enable pytest's **strict mode** for better error catching:

```toml
[tool.pytest.ini_options]
strict = true  # Enables all strictness options
```

Individual strictness options:
- `strict_config = true` - Unknown config options raise errors
- `strict_markers = true` - Unknown markers raise errors
- `strict_parametrization_ids = true` - Invalid parametrize IDs raise errors
- `strict_xfail = true` - xfail with wrong exception raises errors

## Fixtures

### What Are Fixtures?
Fixtures provide a **defined, reliable, and consistent context** for tests:
- Set up test environment (databases, API clients, test data)
- Define the **arrange** phase of tests
- Automatic cleanup after tests complete

### Basic Fixture Usage

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from tests.factories import UserFactory

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Configure Polyfactory to use this session
    from tests.factories.base import BaseFactory
    BaseFactory.__session__ = session
    
    yield session  # Test runs here
    
    session.close()
    Base.metadata.drop_all(engine)

def test_create_user(db_session):
    """Test user creation using Polyfactory."""
    user = UserFactory.create_sync()
    assert user.id is not None
    assert "@" in user.email
```

### Fixture Scopes
Control how often fixtures are created:

- **`scope="function"`** (default) - Once per test function
- **`scope="class"`** - Once per test class
- **`scope="module"`** - Once per test module
- **`scope="package"`** - Once per test package
- **`scope="session"`** - Once per entire test session

```python
@pytest.fixture(scope="session")
def db_engine():
    """Create database engine once for entire test session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create a new session for each test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
```

### Fixture Dependency
Fixtures can depend on other fixtures:

```python
from tests.factories import UserFactory

@pytest.fixture
def user(db_session):
    """Create a test user using Polyfactory."""
    return UserFactory.create_sync()

@pytest.fixture
def auth_token(user):
    return create_access_token(user.id)

def test_protected_endpoint(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 200
```

### Autouse Fixtures
Fixtures that run automatically for all tests:

```python
@pytest.fixture(autouse=True)
def reset_database(db_session):
    """Automatically clear database before each test."""
    yield
    db_session.query(User).delete()
    db_session.query(Sneaker).delete()
    db_session.commit()
```

**Use sparingly** - explicit is better than implicit!

### conftest.py
Place shared fixtures in `conftest.py` files:
- Root `conftest.py` - Available to all tests
- Directory `conftest.py` - Available to tests in that directory and subdirectories

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Database session fixture."""
    # Setup code
    yield session
    # Teardown code
```

## Assertions

### Use Plain `assert` Statements
pytest provides **detailed assertion introspection** - no need for `self.assertEqual()`:

```python
def test_user_creation():
    user = create_user("test@example.com")
    
    # Simple assertions
    assert user.email == "test@example.com"
    assert user.is_active
    assert user.created_at is not None
    
    # Complex assertions
    assert len(user.sneakers) == 0
    assert "test" in user.email.lower()
```

**Assertion output** is automatically detailed:
```
>       assert user.email == "wrong@example.com"
E       assert 'test@example.com' == 'wrong@example.com'
E         - wrong@example.com
E         + test@example.com
```

### Comparing Floats
Use `pytest.approx()` for floating-point comparisons:

```python
def test_price_calculation():
    price = calculate_price(100, 0.15)  # 15% discount
    assert price == pytest.approx(85.0)
    
    # With tolerance
    assert price == pytest.approx(85.0, rel=0.01)  # 1% relative tolerance
```

### Testing Exceptions
Use `pytest.raises()` context manager:

```python
def test_invalid_user_creation():
    with pytest.raises(ValueError) as excinfo:
        create_user("invalid-email")
    
    assert "Invalid email" in str(excinfo.value)

# Match exception message with regex
def test_duplicate_user():
    with pytest.raises(IntegrityError, match=r"UNIQUE constraint"):
        create_user("duplicate@example.com")
        create_user("duplicate@example.com")
```

### Testing for Warnings
Use `pytest.warns()`:

```python
def test_deprecated_function():
    with pytest.warns(DeprecationWarning):
        legacy_function()
```

## Parametrization

### Parametrize Test Functions
Run the same test with different inputs:

```python
@pytest.mark.parametrize("email,expected_valid", [
    ("valid@example.com", True),
    ("another@test.co.uk", True),
    ("invalid.email", False),
    ("@nodomain.com", False),
    ("no@domain", False),
])
def test_email_validation(email, expected_valid):
    result = validate_email(email)
    assert result == expected_valid
```

**Output**: 5 separate test cases are run.

### Parametrize with Multiple Arguments

```python
@pytest.mark.parametrize("username,password,expected_status", [
    ("user1", "correct_pass", 200),
    ("user1", "wrong_pass", 401),
    ("nonexistent", "any_pass", 401),
])
def test_login(client, username, password, expected_status):
    response = client.post("/auth/login", json={
        "username": username,
        "password": password
    })
    assert response.status_code == expected_status
```

### Stack Parametrizations
Create all combinations:

```python
@pytest.mark.parametrize("user_role", ["admin", "user", "guest"])
@pytest.mark.parametrize("http_method", ["GET", "POST", "PUT", "DELETE"])
def test_endpoint_permissions(client, user_role, http_method):
    # 12 test cases total (3 roles × 4 methods)
    pass
```

### Parametrize with IDs
Give descriptive names to test cases:

```python
@pytest.mark.parametrize("size,price", [
    (8, 100),
    (9, 120),
    (10, 150),
], ids=["size-8", "size-9", "size-10"])
def test_sneaker_pricing(size, price):
    assert calculate_price(size) == price
```

### Parametrize Fixtures
Parametrize fixtures to create multiple versions:

```python
@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def db_connection(request):
    """Test against multiple database backends."""
    db_type = request.param
    connection = create_connection(db_type)
    yield connection
    connection.close()

def test_user_crud(db_connection):
    # Runs 3 times - once for each DB
    pass
```

### Mark Individual Parameters
Mark specific parameter sets:

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    pytest.param(4, 15, marks=pytest.mark.xfail),  # Known bug
    (5, 25),
])
def test_square(input, expected):
    assert square(input) == expected
```

## Mocking & Monkeypatching

### The `monkeypatch` Fixture
Safely patch functions, attributes, environment variables, and more:

```python
def test_api_call(monkeypatch):
    # Mock a function
    def mock_api_call(*args, **kwargs):
        return {"status": "success", "data": []}
    
    monkeypatch.setattr("requests.get", mock_api_call)
    
    result = fetch_data_from_api()
    assert result["status"] == "success"
```

### Monkeypatch Methods

**`setattr(obj, name, value)`** - Set/override attribute:
```python
monkeypatch.setattr(Path, "home", lambda: Path("/fake/home"))
monkeypatch.setattr("os.getenv", lambda key: "mocked_value")
```

**`delattr(obj, name)`** - Delete attribute:
```python
monkeypatch.delattr("requests.sessions.Session.request")
```

**`setitem(dict, name, value)`** - Set dictionary item:
```python
monkeypatch.setitem(app.config, "DEBUG", True)
```

**`delitem(dict, name)`** - Delete dictionary item:
```python
monkeypatch.delitem(os.environ, "API_KEY", raising=False)
```

**`setenv(name, value)`** - Set environment variable:
```python
monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
```

**`delenv(name)`** - Delete environment variable:
```python
monkeypatch.delenv("AWS_SECRET_KEY", raising=False)
```

**`syspath_prepend(path)`** - Prepend to sys.path:
```python
monkeypatch.syspath_prepend("/custom/module/path")
```

**`chdir(path)`** - Change working directory:
```python
monkeypatch.chdir("/tmp")
```

### Mock Return Objects
Create mock classes for complex return values:

```python
class MockResponse:
    status_code = 200
    
    @staticmethod
    def json():
        return {"id": 1, "name": "Test Sneaker"}

def test_fetch_sneaker(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()
    
    monkeypatch.setattr("requests.get", mock_get)
    
    sneaker = fetch_sneaker_from_api(1)
    assert sneaker["name"] == "Test Sneaker"
```

### Monkeypatch as Fixture
Share patches across tests:

```python
@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email sending for all tests."""
    sent_emails = []
    
    def fake_send_email(to, subject, body):
        sent_emails.append({"to": to, "subject": subject})
        return True
    
    monkeypatch.setattr("email_service.send_email", fake_send_email)
    return sent_emails

def test_user_registration(client, mock_email_service):
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "securepass"
    })
    assert response.status_code == 201
    assert len(mock_email_service) == 1
    assert mock_email_service[0]["to"] == "new@example.com"
```

### Global Patches (Autouse)
Prevent unwanted side effects in all tests:

```python
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Prevent all HTTP requests during tests."""
    monkeypatch.delattr("requests.sessions.Session.request")
```

### Context Manager for Limited Scope
Apply patches only in specific blocks:

```python
def test_with_limited_patch(monkeypatch):
    # Normal code here
    
    with monkeypatch.context() as m:
        m.setattr("time.sleep", lambda x: None)
        # time.sleep is mocked only here
        some_function_that_sleeps()
    
    # time.sleep works normally again
```

## Markers

### Built-in Markers

**`@pytest.mark.skip`** - Skip a test:
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass
```

**`@pytest.mark.skipif`** - Conditional skip:
```python
import sys

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_syntax():
    pass

@pytest.mark.skipif(not has_database(), reason="Database not available")
def test_database_query():
    pass
```

**`@pytest.mark.xfail`** - Expected to fail:
```python
@pytest.mark.xfail(reason="Known bug #123")
def test_buggy_feature():
    assert buggy_function() == expected_value

@pytest.mark.xfail(raises=RuntimeError)
def test_known_error():
    raise RuntimeError("This is expected")
```

**`@pytest.mark.parametrize`** - See Parametrization section above.

### Custom Markers
Define custom markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
    "unit: unit tests",
    "api: API endpoint tests",
]
```

Use custom markers:
```python
@pytest.mark.slow
@pytest.mark.integration
def test_full_workflow():
    # Long-running integration test
    pass

@pytest.mark.unit
def test_pure_function():
    assert add(2, 3) == 5
```

Run tests by marker:
```bash
pytest -m "unit"                    # Only unit tests
pytest -m "not slow"                # Skip slow tests
pytest -m "integration and not slow" # Integration but not slow
```

## Testing FastAPI Applications

### Test Client Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """FastAPI test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Testing API Endpoints

```python
from tests.factories import UserFactory

def test_create_user(client):
    # Use factory to generate valid test data
    user_data = {
        "email": UserFactory.__faker__.email(),
        "password": "securepass123",
        "username": UserFactory.__faker__.user_name()
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "password" not in data  # Should not return password

def test_get_user_unauthorized(client, db_session):
    # Create a user first
    user = UserFactory.create_sync()
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 401

def test_get_user_authorized(client, auth_token, user):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(f"/api/users/{user.id}", headers=headers)
    assert response.status_code == 200
```

### Testing with Authentication

```python
from tests.factories import UserFactory

@pytest.fixture
def test_user(db_session):
    """Create a test user using Polyfactory."""
    return UserFactory.create_sync()

@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for test user."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint(client, auth_headers):
    response = client.get("/api/protected", headers=auth_headers)
    assert response.status_code == 200
```

## Testing Database Operations

### Test CRUD Operations

```python
from tests.factories import SneakerFactory, UserFactory

def test_create_sneaker(db_session):
    """Test creating a sneaker with Polyfactory."""
    sneaker = SneakerFactory.create_sync()
    
    assert sneaker.id is not None
    assert sneaker.created_at is not None
    assert sneaker.brand in ["Nike", "Adidas", "Puma", "Reebok", "New Balance"]

def test_read_sneaker(db_session):
    """Test reading a sneaker."""
    test_sneaker = SneakerFactory.create_sync()
    
    sneaker = db_session.query(Sneaker).filter_by(id=test_sneaker.id).first()
    assert sneaker is not None
    assert sneaker.brand == test_sneaker.brand

def test_update_sneaker(db_session):
    """Test updating a sneaker."""
    test_sneaker = SneakerFactory.create_sync()
    test_sneaker.price = 250.00
    db_session.commit()
    
    sneaker = db_session.query(Sneaker).get(test_sneaker.id)
    assert sneaker.price == 250.00

def test_delete_sneaker(db_session):
    """Test deleting a sneaker."""
    test_sneaker = SneakerFactory.create_sync()
    sneaker_id = test_sneaker.id
    db_session.delete(test_sneaker)
    db_session.commit()
    
    sneaker = db_session.query(Sneaker).get(sneaker_id)
    assert sneaker is None
```

### Test Relationships

```python
from tests.factories import UserFactory, SneakerFactory

def test_user_sneakers_relationship(db_session):
    """Test user-sneaker relationship with Polyfactory."""
    user = UserFactory.create_sync()
    
    # Create multiple sneakers for the user
    sneakers = SneakerFactory.create_batch_sync(size=3, owner_id=user.id)
    
    db_session.refresh(user)
    assert len(user.sneakers) == 3
    for sneaker in sneakers:
        assert sneaker in user.sneakers
        assert sneaker.owner_id == user.id
```

### Test Unique Constraints

```python
from tests.factories import UserFactory
from sqlalchemy.exc import IntegrityError

def test_unique_email(db_session):
    """Test email uniqueness constraint."""
    # Create first user
    user1 = UserFactory.create_sync(email="duplicate@example.com")
    
    # Try to create second user with same email
    with pytest.raises(IntegrityError):
        UserFactory.create_sync(email="duplicate@example.com")
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Run tests matching pattern
pytest -k "user"  # Runs all tests with "user" in name

# Run tests by marker
pytest -m "unit"
pytest -m "not slow"

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show local variables in tracebacks
pytest -l

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Output Options

```bash
# Short traceback
pytest --tb=short

# No traceback
pytest --tb=no

# Show print statements
pytest -s

# Coverage report (requires pytest-cov)
pytest --cov=. --cov-report=html
```

## Using Polyfactory with pytest

### Overview
Polyfactory is integrated throughout our test suite for **automatic test data generation**. Instead of manually creating model instances, use factories to generate realistic, randomized test data.

### Key Benefits
1. **Less boilerplate** - No manual object creation
2. **Realistic data** - Uses Faker for lifelike values
3. **Type-safe** - Based on model type hints
4. **Relationships** - Automatically handles foreign keys
5. **Customizable** - Override specific fields when needed
6. **Reproducible** - Seed randomness for deterministic tests

### Quick Reference

```python
from tests.factories import UserFactory, SneakerFactory

# Create single instance (not persisted)
user = UserFactory.build()

# Create and persist to database
user = UserFactory.create_sync()

# Create multiple instances
users = UserFactory.batch(size=10)  # Not persisted
users = UserFactory.create_batch_sync(size=10)  # Persisted

# Override specific fields
user = UserFactory.create_sync(
    email="specific@example.com",
    is_active=True
)

# Create with relationships
sneaker = SneakerFactory.create_sync(
    owner_id=user.id,
    brand="Nike"
)
```

### Factory Setup in conftest.py

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database import Base
from tests.factories.base import BaseFactory

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    
    # Configure Polyfactory to use this session
    BaseFactory.__session__ = session
    
    yield session
    
    session.close()
```

### Common Factory Patterns

**Creating test fixtures with factories**:
```python
@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    return AdminUserFactory.create_sync()

@pytest.fixture
def user_with_sneakers(db_session):
    """Create a user with multiple sneakers."""
    user = UserFactory.create_sync()
    SneakerFactory.create_batch_sync(size=5, owner_id=user.id)
    db_session.refresh(user)
    return user
```

**Using factories in tests**:
```python
def test_sneaker_creation(db_session):
    """Test sneaker is properly created."""
    sneaker = SneakerFactory.create_sync()
    assert sneaker.id is not None
    assert 50.0 <= sneaker.price <= 500.0

def test_specific_sneaker(db_session):
    """Test with specific sneaker attributes."""
    sneaker = SneakerFactory.create_sync(
        brand="Nike",
        model="Air Jordan 1",
        price=200.00
    )
    assert sneaker.brand == "Nike"
```

**See [copilot-backend-polyfactory-instructions.md](./copilot-backend-polyfactory-instructions.md) for complete documentation.**

## Best Practices Summary

### Test Structure
1. ✅ Use **"tests outside application code"** layout
2. ✅ Follow **naming conventions** (`test_*.py`, `test_*()`)
3. ✅ Use **`importlib` import mode** for new projects
4. ✅ Organize tests by feature/module

### Fixtures
5. ✅ Use **fixtures** for setup/teardown
6. ✅ Choose appropriate **scopes** (function, class, module, session)
7. ✅ Place shared fixtures in **`conftest.py`**
8. ✅ Use **explicit fixture dependencies**
9. ✅ Use **`autouse=True`** sparingly

### Assertions
10. ✅ Use plain **`assert`** statements
11. ✅ Use **`pytest.approx()`** for floats
12. ✅ Use **`pytest.raises()`** for exceptions
13. ✅ Test error messages with **`match=`** parameter

### Parametrization
14. ✅ Use **`@pytest.mark.parametrize`** for multiple test cases
15. ✅ Give test cases **descriptive IDs**
16. ✅ Use **fixture parametrization** for complex scenarios

### Mocking
17. ✅ Use **`monkeypatch`** fixture for patching
18. ✅ Mock **external dependencies** (APIs, file systems, etc.)
19. ✅ Use **autouse fixtures** to prevent unwanted side effects
20. ✅ Clean up patches automatically (monkeypatch handles this)

### Markers
21. ✅ Define **custom markers** in config
22. ✅ Use **`@pytest.mark.skip`** for incomplete tests
23. ✅ Use **`@pytest.mark.xfail`** for known bugs
24. ✅ Mark **slow/integration** tests separately

### FastAPI Testing
25. ✅ Use **`TestClient`** from `fastapi.testclient`
26. ✅ Override **dependencies** with `app.dependency_overrides`
27. ✅ Use **in-memory database** (SQLite) for tests
28. ✅ Create **fresh database** for each test

### Database Testing
29. ✅ Use **transactions** and **rollback** for isolation
30. ✅ Test **CRUD operations** thoroughly
31. ✅ Test **relationships** between models
32. ✅ Test **constraints** (unique, foreign keys, etc.)

### Code Quality
33. ✅ Enable **strict mode** in pytest config
34. ✅ Keep tests **small and focused**
35. ✅ Test **one thing per test function**
36. ✅ Use **descriptive test names**
37. ✅ Write tests **before or alongside** code (TDD)

### Polyfactory
38. ✅ Use **factories** for all test data generation
39. ✅ Configure **BaseFactory** with common settings
40. ✅ Use **`create_sync()`** for persisted test data
41. ✅ Use **`build()`** for non-persisted objects
42. ✅ Override **specific fields** when needed
43. ✅ Use **batch methods** for multiple instances

### Anti-Patterns to Avoid
44. ❌ Don't use **`pytest-runner`** or `python setup.py test` (deprecated)
45. ❌ Don't **hardcode** test data - use factories instead
46. ❌ Don't use **`sleep()`** - mock time instead
47. ❌ Don't test **implementation details** - test behavior
48. ❌ Don't make tests **depend on each other**
49. ❌ Don't **share mutable state** between tests
50. ❌ Don't **manually create** model instances - use Polyfactory
51. ❌ Don't **forget to set** `__session__` on BaseFactory in fixtures

## Additional Resources
- pytest documentation: https://docs.pytest.org/en/stable/
- Polyfactory documentation: https://polyfactory.litestar.dev/latest/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- SQLAlchemy testing: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
- **Polyfactory Guide**: [copilot-backend-polyfactory-instructions.md](./copilot-backend-polyfactory-instructions.md)

## Example Test File Structure

```python
# tests/test_users.py
"""Tests for user-related functionality."""

import pytest
from fastapi import status
from models.user import User
from tests.factories import UserFactory

# Fixtures specific to this test module
@pytest.fixture
def test_user(db_session):
    """Create a test user using Polyfactory."""
    return UserFactory.create_sync()

@pytest.fixture
def test_user_data():
    """Sample user data for API requests."""
    return {
        "email": UserFactory.__faker__.email(),
        "username": UserFactory.__faker__.user_name(),
        "password": "securepass123"
    }

# Unit tests
class TestUserModel:
    """Unit tests for User model."""
    
    def test_create_user(self, db_session):
        """Test user creation with Polyfactory."""
        user = UserFactory.create_sync()
        
        assert user.id is not None
        assert "@" in user.email
        assert user.username is not None
    
    def test_create_user_with_specific_email(self, db_session):
        """Test creating user with specific email."""
        user = UserFactory.create_sync(email="specific@example.com")
        assert user.email == "specific@example.com"
    
    def test_password_hashing(self, db_session):
        """Test password is hashed."""
        user = UserFactory.create_sync()
        # Factory sets a known hashed password
        assert user.hashed_password is not None
        assert user.hashed_password.startswith("$2b$")

# Integration tests
class TestUserAPI:
    """Integration tests for user API endpoints."""
    
    def test_register_user(self, client, test_user_data):
        """Test user registration endpoint."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "password" not in data
    
    @pytest.mark.parametrize("field", ["email", "username", "password"])
    def test_register_missing_field(self, client, test_user_data, field):
        """Test registration fails with missing required fields."""
        incomplete_data = test_user_data.copy()
        del incomplete_data[field]
        
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, db_session):
        """Test successful login."""
        # Create user with known password
        user = UserFactory.create_sync(email="test@example.com")
        
        response = client.post("/api/auth/login", json={
            "email": user.email,
            "password": "password"  # Known password from factory
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, db_session):
        """Test login with invalid credentials."""
        user = UserFactory.create_sync()
        
        response = client.post("/api/auth/login", json={
            "email": user.email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

---

**Remember**: Good tests are **fast**, **isolated**, **repeatable**, **self-validating**, and **timely** (F.I.R.S.T principles).

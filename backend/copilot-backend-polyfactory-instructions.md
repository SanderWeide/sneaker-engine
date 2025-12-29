# GitHub Copilot Instructions for Backend Testing with Polyfactory

**IMPORTANT**: When creating test data factories for this backend, always refer to these Polyfactory best practices.

## Project Context
- **Framework**: FastAPI backend with PostgreSQL database
- **ORM**: SQLAlchemy
- **Models**: Pydantic for validation, SQLAlchemy for database
- **Test Data Generation**: Polyfactory

## Polyfactory Documentation Reference
- Full documentation: https://polyfactory.litestar.dev/latest/

## What is Polyfactory?

Polyfactory is a simple and powerful **mock data generation library** based on type hints. It generates realistic test data automatically by analyzing your model's type annotations.

**Supports**:
- Python dataclasses
- TypedDicts
- Pydantic models (v1 and v2)
- SQLAlchemy models (1.4 and 2.x)
- Msgspec Structs
- Attrs models
- Odmantic and Beanie ODM models

**Key Benefits**:
- ✅ **Zero configuration** - works out of the box
- ✅ **Type-safe** - uses type hints for data generation
- ✅ **Highly customizable** - control exactly what data is generated
- ✅ **Database persistence** - built-in sync/async persistence handlers
- ✅ **Faker integration** - uses Faker library for realistic data
- ✅ **Relationship handling** - automatically handles foreign keys and relationships

## Installation

```bash
pip install polyfactory
```

For SQLAlchemy support (our use case):
```bash
pip install polyfactory[sqlalchemy]
```

## Basic Usage

### Simple Example

```python
from dataclasses import dataclass
from polyfactory.factories import DataclassFactory

@dataclass
class Person:
    name: str
    age: int
    email: str

class PersonFactory(DataclassFactory[Person]):
    __model__ = Person

# Generate a single instance
person = PersonFactory.build()
assert isinstance(person.name, str)
assert isinstance(person.age, int)
assert isinstance(person.email, str)

# Generate multiple instances
people = PersonFactory.batch(size=10)
assert len(people) == 10
```

### Generic Syntax (Recommended)

Since v2.13.0, you can omit `__model__` and only use the generic parameter:

```python
class PersonFactory(DataclassFactory[Person]):
    # __model__ not needed - inferred from generic type
    pass
```

## Factory Types

### For SQLAlchemy Models (Our Primary Use Case)

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    username: Mapped[str]

class UserFactory(SQLAlchemyFactory[User]):
    pass

# Generate model instance
user = UserFactory.build()
assert isinstance(user, User)
```

### For Pydantic Models

```python
from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory

class User(BaseModel):
    name: str
    age: int
    email: str

class UserFactory(ModelFactory[User]):
    pass

user = UserFactory.build()
assert isinstance(user, User)
```

## Factory Methods

### Core Methods

**`build(**kwargs)`** - Create a single instance (in memory, not persisted)
```python
user = UserFactory.build()
user_with_email = UserFactory.build(email="test@example.com")
```

**`batch(size, **kwargs)`** - Create multiple instances
```python
users = UserFactory.batch(size=10)
users_with_role = UserFactory.batch(size=5, role="admin")
```

**`coverage(**kwargs)`** - Create an instance using every field variation (for testing edge cases)
```python
# Generates instances covering all possible type variations
users = UserFactory.coverage()
```

### Persistence Methods (SQLAlchemy)

**`create_sync(**kwargs)`** - Build and persist a single instance synchronously
```python
user = UserFactory.create_sync()
# User is now saved to the database
```

**`create_batch_sync(size, **kwargs)`** - Build and persist multiple instances synchronously
```python
users = UserFactory.create_batch_sync(size=10)
# All 10 users are now saved to the database
```

**`create_async(**kwargs)`** - Build and persist a single instance asynchronously
```python
user = await UserFactory.create_async()
```

**`create_batch_async(size, **kwargs)`** - Build and persist multiple instances asynchronously
```python
users = await UserFactory.create_batch_async(size=10)
```

## Field Customization

### Hardcoded Values

```python
class UserFactory(SQLAlchemyFactory[User]):
    email = "test@example.com"  # Always this value
    
user = UserFactory.build()
assert user.email == "test@example.com"
```

### The `Use` Field

Use `Use` to call a function to generate a value:

```python
from polyfactory import Use

class UserFactory(SQLAlchemyFactory[User]):
    # Use random.choice to pick from a list
    role = Use(UserFactory.__random__.choice, ["admin", "user", "guest"])
    
    # Use Faker for realistic data
    email = Use(lambda: UserFactory.__faker__.email())

user = UserFactory.build()
assert user.role in ["admin", "user", "guest"]
```

**Best Practice**: Use `cls.__random__` instead of `random.choice()` for seeded randomness:

```python
class UserFactory(SQLAlchemyFactory[User]):
    @classmethod
    def role(cls) -> str:
        return cls.__random__.choice(["admin", "user", "guest"])
```

### The `Ignore` Field

Ignore specific fields (they won't be generated):

```python
from polyfactory import Ignore

class UserFactory(SQLAlchemyFactory[User]):
    password_hash = Ignore()  # Don't generate password_hash
    
user = UserFactory.build()
assert not hasattr(user, 'password_hash') or user.password_hash is None
```

### The `Require` Field

Make a field required as a build argument:

```python
from polyfactory import Require
import pytest
from polyfactory.exceptions import MissingBuildKwargException

class UserFactory(SQLAlchemyFactory[User]):
    email = Require()  # Must be provided
    
# This works
user = UserFactory.build(email="test@example.com")

# This raises MissingBuildKwargException
with pytest.raises(MissingBuildKwargException):
    UserFactory.build()
```

### The `PostGenerated` Field

Generate a field based on other already-generated fields:

```python
from polyfactory import PostGenerated
from datetime import datetime, timedelta
from typing import Any

def calculate_end_date(name: str, values: dict[str, Any], *args, **kwargs) -> datetime:
    """Calculate end_date as start_date + 7 days."""
    return values["start_date"] + timedelta(days=7)

class EventFactory(SQLAlchemyFactory[Event]):
    end_date = PostGenerated(calculate_end_date)
    
event = EventFactory.build()
assert event.end_date == event.start_date + timedelta(days=7)
```

**Signature**: `callback(name: str, values: dict[str, Any], *args, **kwargs) -> Any`
- `name`: Field name being generated
- `values`: Dictionary of already-generated field values
- Returns: The value for the field

### Factories as Fields

Use another factory as a field value:

```python
class AddressFactory(SQLAlchemyFactory[Address]):
    city = Use(lambda: AddressFactory.__random__.choice(["NYC", "LA", "Chicago"]))

class UserFactory(SQLAlchemyFactory[User]):
    address = AddressFactory  # Will call AddressFactory.build()
    
user = UserFactory.build()
assert isinstance(user.address, Address)

# Can override sub-factory fields
user_with_custom_city = UserFactory.build(address={"city": "Boston"})
assert user_with_custom_city.address.city == "Boston"
```

## Configuration Options

All configuration is done via class attributes starting with `__`:

### `__random_seed__` - Seed for Reproducible Data

```python
class UserFactory(SQLAlchemyFactory[User]):
    __random_seed__ = 12345
    
    @classmethod
    def username(cls) -> str:
        return cls.__random__.choice(["alice", "bob", "charlie"])

# Results are now deterministic
assert UserFactory.build().username == "alice"
assert UserFactory.build().username == "charlie"
assert UserFactory.build().username == "alice"  # Repeats
```

### `__random__` - Set Random Instance Directly

```python
from random import Random

class UserFactory(SQLAlchemyFactory[User]):
    __random__ = Random(999)
```

### `__faker__` - Configure Faker Instance

```python
from faker import Faker

class UserFactory(SQLAlchemyFactory[User]):
    __faker__ = Faker(locale="es_ES")  # Spanish locale
    __random_seed__ = 10  # For deterministic results
    
    @classmethod
    def name(cls) -> str:
        return cls.__faker__.name()

user = UserFactory.build()
# name will be a Spanish name
```

### `__randomize_collection_length__` - Random Collection Sizes

```python
class UserFactory(SQLAlchemyFactory[User]):
    __randomize_collection_length__ = True
    __min_collection_length__ = 2
    __max_collection_length__ = 5

user = UserFactory.build()
assert 2 <= len(user.tags) <= 5  # Random number of tags
```

**Default**: Only 1 item generated per collection

### `__allow_none_optionals__` - Control Optional Handling

```python
class UserFactory(SQLAlchemyFactory[User]):
    __allow_none_optionals__ = False  # Never generate None for Optional fields

user = UserFactory.build()
assert user.middle_name is not None  # Even if Optional[str]
```

**Default**: `True` (None can be randomly chosen for optional fields)

### `__check_model__` - Validate Factory Fields

```python
class UserFactory(SQLAlchemyFactory[User]):
    __check_model__ = True  # Raises error if unknown_field isn't on User model
    unknown_field = Use(lambda: "value")  # ConfigurationException raised
```

**Default**: `True` in v3+ (recommended to keep enabled)

### `__use_defaults__` - Use Model Default Values

```python
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(default="user")
    is_active: Mapped[bool] = mapped_column(default=True)

class UserFactory(SQLAlchemyFactory[User]):
    __use_defaults__ = True  # Use model defaults

user = UserFactory.build()
assert user.role == "user"  # Uses default
assert user.is_active is True  # Uses default
```

**Default**: `False` (generates random values even if defaults exist)

### `__use_examples__` - Use Pydantic Examples (Pydantic v2 only)

```python
from pydantic import BaseModel, Field

class Payment(BaseModel):
    currency: str = Field(examples=["USD", "EUR", "GBP"])

class PaymentFactory(ModelFactory[Payment]):
    __use_examples__ = True

payment = PaymentFactory.build()
assert payment.currency in ["USD", "EUR", "GBP"]
```

### `__by_name__` - Validation Aliases (Pydantic v2 only)

```python
from pydantic import BaseModel, Field, AliasPath

class User(BaseModel):
    username: str = Field(..., validation_alias="user_name")
    email: str = Field(..., validation_alias=AliasPath("contact", "email"))

class UserFactory(ModelFactory[User]):
    __by_name__ = True  # Use field names instead of aliases
    
    username = "john_doe"  # Set by field name, not alias

user = UserFactory.build()
assert user.username == "john_doe"
```

## SQLAlchemy-Specific Features

### Relationships

**Default**: `__set_relationships__ = True` (automatically handles relationships)

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship("Book")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

class AuthorFactory(SQLAlchemyFactory[Author]):
    __set_relationships__ = True  # This is the default

author = AuthorFactory.build()
assert len(author.books) > 0
assert isinstance(author.books[0], Book)

# Disable relationships
class AuthorFactoryNoRelationships(SQLAlchemyFactory[Author]):
    __set_relationships__ = False

author = AuthorFactoryNoRelationships.build()
assert author.books == []
```

**Note**: When using `create_sync`/`create_async`, foreign keys are overwritten by SQLAlchemy ORM.

### Association Proxies

**Default**: `__set_association_proxy__ = True`

```python
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    keywords: AssociationProxy[list["Keyword"]] = association_proxy(
        "user_keyword_associations", "keyword"
    )

class UserFactory(SQLAlchemyFactory[User]):
    __set_association_proxy__ = True  # This is the default

user = UserFactory.build()
assert len(user.keywords) > 0
```

### Database Persistence

Set `__session__` for sync persistence or `__async_session__` for async:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Setup database
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
session = Session(engine)

class UserFactory(SQLAlchemyFactory[User]):
    __session__ = session  # Or a callable that returns a session
    __set_relationships__ = True

# Creates and persists to database
user = UserFactory.create_sync()
assert user.id is not None  # Has a database-assigned ID

# Batch persistence
users = UserFactory.create_batch_sync(10)
assert all(u.id is not None for u in users)
```

**Async Example**:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
async_session = AsyncSession(async_engine)

class UserFactory(SQLAlchemyFactory[User]):
    __async_session__ = async_session

# Async persistence
user = await UserFactory.create_async()
users = await UserFactory.create_batch_async(10)
```

### Custom Persistence Handlers

```python
from polyfactory import SyncPersistenceProtocol, AsyncPersistenceProtocol

class CustomSyncHandler(SyncPersistenceProtocol[User]):
    def save(self, data: User) -> User:
        # Custom save logic (e.g., with additional logging)
        session.add(data)
        session.commit()
        print(f"Saved user: {data.email}")
        return data
    
    def save_many(self, data: list[User]) -> list[User]:
        session.add_all(data)
        session.commit()
        return data

class UserFactory(SQLAlchemyFactory[User]):
    __sync_persistence__ = CustomSyncHandler
```

### Custom Column Type Mapping

Map custom SQLAlchemy column types to Python types:

```python
from sqlalchemy import types
from decimal import Decimal

class Location(types.TypeEngine):
    cache_ok = True

class Place(Base):
    __tablename__ = "places"
    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[tuple[Decimal, Decimal]] = mapped_column(Location)

class PlaceFactory(SQLAlchemyFactory[Place]):
    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
        mapping = super().get_sqlalchemy_types()
        mapping[Location] = cls.__faker__.latlng  # Use Faker's lat/lng
        return mapping

place = PlaceFactory.build()
assert isinstance(place.location, tuple)
```

## Imperative Factory Creation

Dynamically create factories at runtime:

```python
# Create a factory imperatively
PetFactory = DataclassFactory.create_factory(model=Pet)
pet = PetFactory.build()

# Create a sub-factory with overrides
CatFactory = PetFactory.create_factory(species="Cat")
cat = CatFactory.build()
assert cat.species == "Cat"
```

## Default Factories

Set a factory as the default for a type:

```python
class PetFactory(DataclassFactory[Pet]):
    __set_as_default_factory_for_type__ = True
    name = Use(DataclassFactory.__random__.choice, ["Fluffy", "Rex", "Whiskers"])

class PersonFactory(DataclassFactory[Person]):
    pass  # Will automatically use PetFactory for Pet fields

person = PersonFactory.build()
assert person.pet.name in ["Fluffy", "Rex", "Whiskers"]
```

## Pytest Integration

### Register as Pytest Fixture

```python
from polyfactory.pytest_plugin import register_fixture

@register_fixture
class UserFactory(SQLAlchemyFactory[User]):
    pass

def test_user(user_factory: UserFactory) -> None:
    user = user_factory.build()
    assert isinstance(user, User)
```

### Register with Custom Name

```python
@register_fixture(name="custom_user_factory")
class UserFactory(SQLAlchemyFactory[User]):
    pass

def test_user(custom_user_factory: UserFactory) -> None:
    user = custom_user_factory.build()
    assert isinstance(user, User)
```

### Register Separately

```python
class UserFactory(SQLAlchemyFactory[User]):
    pass

# In conftest.py
register_fixture(UserFactory)
```

## Best Practices for Our Backend

### 1. Create a Base Factory for Common Settings

```python
# tests/factories/base.py
from sqlalchemy.orm import Session
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, T

class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True  # Important!
    __set_relationships__ = True
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 3
    __check_model__ = True
    __allow_none_optionals__ = False  # Avoid None in tests

# Set session in conftest.py
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    BaseFactory.__session__ = session
    yield session
    session.close()
```

### 2. Organize Factories by Domain

```
tests/
├── conftest.py
└── factories/
    ├── __init__.py
    ├── base.py
    ├── user_factory.py
    ├── sneaker_factory.py
    └── proposition_factory.py
```

### 3. Define Realistic Factory Defaults

```python
# tests/factories/user_factory.py
from tests.factories.base import BaseFactory
from models.user import User
from polyfactory import Use

class UserFactory(BaseFactory[User]):
    email = Use(lambda: UserFactory.__faker__.email())
    username = Use(lambda: UserFactory.__faker__.user_name())
    
    @classmethod
    def hashed_password(cls) -> str:
        # Use a known hash for testing
        return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xELq1aDDq"  # "password"
```

### 4. Create Specific Factories for Test Scenarios

```python
class AdminUserFactory(UserFactory):
    role = "admin"
    is_active = True

class InactiveUserFactory(UserFactory):
    is_active = False
    deleted_at = Use(lambda: UserFactory.__faker__.date_time_this_year())
```

### 5. Use Factories in Fixtures

```python
# tests/conftest.py
import pytest
from tests.factories import UserFactory, SneakerFactory

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    return UserFactory.create_sync()

@pytest.fixture
def test_user_with_sneakers(db_session):
    """Create a user with sneakers."""
    user = UserFactory.create_sync()
    SneakerFactory.create_batch_sync(size=5, owner_id=user.id)
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    """Create an admin user."""
    return AdminUserFactory.create_sync()
```

### 6. Override Fields in Tests

```python
def test_user_with_specific_email(db_session):
    user = UserFactory.create_sync(email="specific@example.com")
    assert user.email == "specific@example.com"
    assert user.id is not None  # Was persisted

def test_sneaker_for_user(db_session, test_user):
    sneaker = SneakerFactory.create_sync(
        owner_id=test_user.id,
        brand="Nike",
        model="Air Jordan 1"
    )
    assert sneaker.owner_id == test_user.id
    assert sneaker.brand == "Nike"
```

### 7. Use Coverage for Edge Cases

```python
def test_user_edge_cases():
    # Generates users with all type variations
    users = UserFactory.coverage()
    
    # Test each variation
    for user in users:
        # Your edge case testing logic
        assert validate_user(user)
```

### 8. Seeded Factories for Reproducible Tests

```python
class ReproducibleUserFactory(UserFactory):
    __random_seed__ = 12345

def test_deterministic():
    # Always generates the same data
    user1 = ReproducibleUserFactory.build()
    user2 = ReproducibleUserFactory.build()
    # user1 and user2 have predictable values
```

### 9. Factories for Relationships

```python
class SneakerFactory(BaseFactory[Sneaker]):
    owner = UserFactory  # Automatically creates a user
    
    brand = Use(lambda: SneakerFactory.__random__.choice([
        "Nike", "Adidas", "Puma", "Reebok", "New Balance"
    ]))
    
    @classmethod
    def price(cls) -> float:
        return cls.__random__.uniform(50.0, 500.0)

# In tests
sneaker = SneakerFactory.create_sync()
assert sneaker.owner is not None
assert isinstance(sneaker.owner, User)

# Override the relationship
specific_user = UserFactory.create_sync(email="owner@example.com")
sneaker = SneakerFactory.create_sync(owner_id=specific_user.id)
assert sneaker.owner.email == "owner@example.com"
```

### 10. Handle Unique Constraints

```python
from polyfactory import Use
import uuid

class UserFactory(BaseFactory[User]):
    # Ensure unique emails
    email = Use(lambda: f"{uuid.uuid4().hex}@example.com")
    
    # Or use Faker's unique generator
    @classmethod
    def username(cls) -> str:
        return cls.__faker__.unique.user_name()

# Create many users without conflicts
users = UserFactory.create_batch_sync(100)
assert len(set(u.email for u in users)) == 100  # All unique
```

## Common Patterns

### Factory Inheritance

```python
class BaseUserFactory(BaseFactory[User]):
    is_active = True
    role = "user"

class AdminFactory(BaseUserFactory):
    role = "admin"
    
class GuestFactory(BaseUserFactory):
    role = "guest"
```

### Factory with Enum Fields

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserFactory(BaseFactory[User]):
    role = Use(UserFactory.__random__.choice, list(UserRole))
    
    # Or specific role
    @classmethod
    def role(cls) -> UserRole:
        return cls.__random__.choice([UserRole.USER, UserRole.ADMIN])
```

### Factory with Date/Time Fields

```python
from datetime import datetime, timedelta

class EventFactory(BaseFactory[Event]):
    # Recent date
    created_at = Use(lambda: EventFactory.__faker__.date_time_this_month())
    
    # Date in the past
    @classmethod
    def start_date(cls) -> datetime:
        return cls.__faker__.date_time_between(start_date="-30d", end_date="now")
    
    # Future date
    @classmethod  
    def end_date(cls) -> datetime:
        return cls.__faker__.date_time_between(start_date="now", end_date="+30d")
```

### Factory with Complex Nested Structures

```python
class AddressFactory(BaseFactory[Address]):
    street = Use(lambda: AddressFactory.__faker__.street_address())
    city = Use(lambda: AddressFactory.__faker__.city())
    country = Use(lambda: AddressFactory.__faker__.country())

class UserFactory(BaseFactory[User]):
    address = AddressFactory
    
    # Or use PostGenerated for complex logic
    full_address = PostGenerated(
        lambda name, values, *args, **kwargs: 
            f"{values['address'].street}, {values['address'].city}"
    )
```

## Testing Recipes

### Test CRUD Operations with Factories

```python
def test_create_user(db_session):
    user = UserFactory.create_sync()
    
    # Test retrieval
    retrieved = db_session.query(User).filter_by(id=user.id).first()
    assert retrieved is not None
    assert retrieved.email == user.email

def test_update_user(db_session):
    user = UserFactory.create_sync()
    
    # Update
    new_email = "updated@example.com"
    user.email = new_email
    db_session.commit()
    
    # Verify
    db_session.refresh(user)
    assert user.email == new_email

def test_delete_user(db_session):
    user = UserFactory.create_sync()
    user_id = user.id
    
    # Delete
    db_session.delete(user)
    db_session.commit()
    
    # Verify
    assert db_session.query(User).filter_by(id=user_id).first() is None
```

### Test API Endpoints with Factories

```python
from fastapi.testclient import TestClient

def test_get_user(client: TestClient, db_session):
    user = UserFactory.create_sync()
    
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user.email
    assert data["username"] == user.username

def test_create_sneaker(client: TestClient, db_session, auth_headers):
    # Use factory to generate request payload
    sneaker_data = SneakerFactory.build().__dict__
    del sneaker_data['id']  # Remove auto-generated ID
    
    response = client.post(
        "/api/sneakers",
        json=sneaker_data,
        headers=auth_headers
    )
    assert response.status_code == 201
```

### Test Business Logic with Factories

```python
def test_proposition_acceptance(db_session):
    # Setup: Create two users and their sneakers
    user1 = UserFactory.create_sync()
    user2 = UserFactory.create_sync()
    
    sneaker1 = SneakerFactory.create_sync(owner_id=user1.id)
    sneaker2 = SneakerFactory.create_sync(owner_id=user2.id)
    
    # Create proposition
    prop = PropositionFactory.create_sync(
        sender_id=user1.id,
        receiver_id=user2.id,
        offered_sneaker_id=sneaker1.id,
        requested_sneaker_id=sneaker2.id,
        status="pending"
    )
    
    # Test acceptance logic
    accept_proposition(prop.id, user2.id)
    
    db_session.refresh(sneaker1)
    db_session.refresh(sneaker2)
    
    # Verify ownership swap
    assert sneaker1.owner_id == user2.id
    assert sneaker2.owner_id == user1.id
```

### Test Validation with Factories

```python
def test_invalid_email_format():
    with pytest.raises(ValidationError):
        UserFactory.build(email="not-an-email")

def test_price_constraints():
    with pytest.raises(ValidationError):
        SneakerFactory.build(price=-10.0)  # Negative price

def test_required_fields():
    with pytest.raises(MissingBuildKwargException):
        class StrictUserFactory(UserFactory):
            email = Require()
        
        StrictUserFactory.build()  # Missing required email
```

## Anti-Patterns to Avoid

### ❌ Don't Use Global `random` Module

```python
# Bad
import random

class UserFactory(BaseFactory[User]):
    role = random.choice(["admin", "user"])  # Won't be seeded properly

# Good
class UserFactory(BaseFactory[User]):
    role = Use(UserFactory.__random__.choice, ["admin", "user"])
```

### ❌ Don't Hardcode IDs

```python
# Bad
class SneakerFactory(BaseFactory[Sneaker]):
    owner_id = 1  # Hardcoded ID

# Good
class SneakerFactory(BaseFactory[Sneaker]):
    owner = UserFactory  # Let the factory create the relationship
```

### ❌ Don't Share Mutable Defaults

```python
# Bad
class UserFactory(BaseFactory[User]):
    tags = ["tag1"]  # Shared list!

# Good
class UserFactory(BaseFactory[User]):
    tags = Use(lambda: ["tag1", "tag2"])  # New list each time
```

### ❌ Don't Forget to Set `__is_base_factory__`

```python
# Bad - will try to instantiate abstract base
class BaseFactory(SQLAlchemyFactory[T]):
    pass

# Good
class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True  # Won't be instantiated directly
```

### ❌ Don't Mix Build and Persistence Methods

```python
# Bad
user = UserFactory.build()  # Not persisted
sneaker = SneakerFactory.create_sync(owner_id=user.id)  # Foreign key error!

# Good
user = UserFactory.create_sync()  # Persisted
sneaker = SneakerFactory.create_sync(owner_id=user.id)  # Works!
```

## Complete Example: Sneaker Engine Test Factories

```python
# tests/factories/base.py
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, T

class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __set_relationships__ = True
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 3
    __check_model__ = True
    __allow_none_optionals__ = False

# tests/factories/user_factory.py
from polyfactory import Use
from tests.factories.base import BaseFactory
from models.user import User

class UserFactory(BaseFactory[User]):
    email = Use(lambda: UserFactory.__faker__.unique.email())
    username = Use(lambda: UserFactory.__faker__.unique.user_name())
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xELq1aDDq"
    is_active = True

class AdminUserFactory(UserFactory):
    is_superuser = True

# tests/factories/sneaker_factory.py
from polyfactory import Use
from tests.factories.base import BaseFactory
from tests.factories.user_factory import UserFactory
from models.sneaker import Sneaker

class SneakerFactory(BaseFactory[Sneaker]):
    owner = UserFactory
    
    brand = Use(lambda: SneakerFactory.__random__.choice([
        "Nike", "Adidas", "Puma", "Reebok", "New Balance"
    ]))
    
    model = Use(lambda: SneakerFactory.__faker__.word().title())
    
    @classmethod
    def size(cls) -> float:
        return cls.__random__.choice([7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0])
    
    @classmethod
    def price(cls) -> float:
        return round(cls.__random__.uniform(50.0, 500.0), 2)
    
    condition = Use(lambda: SneakerFactory.__random__.choice([
        "New", "Like New", "Excellent", "Good", "Fair"
    ]))

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
    
    # Configure factories to use this session
    BaseFactory.__session__ = session
    
    yield session
    
    session.close()

# tests/test_users.py
from tests.factories.user_factory import UserFactory, AdminUserFactory

def test_create_user(db_session):
    user = UserFactory.create_sync()
    assert user.id is not None
    assert "@" in user.email

def test_admin_user(db_session):
    admin = AdminUserFactory.create_sync()
    assert admin.is_superuser is True

# tests/test_sneakers.py
from tests.factories.user_factory import UserFactory
from tests.factories.sneaker_factory import SneakerFactory

def test_create_sneaker(db_session):
    user = UserFactory.create_sync()
    sneaker = SneakerFactory.create_sync(owner_id=user.id)
    
    assert sneaker.id is not None
    assert sneaker.owner_id == user.id
    assert 50.0 <= sneaker.price <= 500.0

def test_user_with_sneakers(db_session):
    user = UserFactory.create_sync()
    sneakers = SneakerFactory.create_batch_sync(size=5, owner_id=user.id)
    
    db_session.refresh(user)
    assert len(user.sneakers) == 5
```

## Summary: Key Polyfactory Concepts

1. **Zero Config**: Works out of the box with type hints
2. **Factories**: Declarative classes that generate mock data
3. **Methods**: `build()`, `batch()`, `create_sync()`, `create_async()`
4. **Fields**: `Use`, `Ignore`, `Require`, `PostGenerated` for customization
5. **Configuration**: `__random_seed__`, `__faker__`, `__set_relationships__`, etc.
6. **SQLAlchemy**: Built-in support for models, relationships, persistence
7. **Pytest**: `@register_fixture` for easy test integration
8. **Reproducibility**: Seed randomness for deterministic tests
9. **Relationships**: Automatically handles foreign keys and nested objects
10. **Persistence**: Built-in database persistence with sync/async support

## Additional Resources

- Documentation: https://polyfactory.litestar.dev/latest/
- GitHub: https://github.com/litestar-org/polyfactory
- Examples: https://polyfactory.litestar.dev/latest/usage/
- Faker docs: https://faker.readthedocs.io/en/master/

---

**Remember**: Polyfactory makes test data generation **effortless**. Define factories once, use them everywhere, and let type hints do the heavy lifting!

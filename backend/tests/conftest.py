"""Shared pytest fixtures and configuration for all tests."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Tuple, Dict

from database import get_db
from database import Base
from main import app
from auth_utils import get_password_hash
from models.user import User

from tests.factories.user_factory import UserFactory
from auth_utils import create_access_token

# Database URL for testing (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh database engine for each test."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """Create a test client with dependency overrides."""    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_password() -> str:
    """Return a standard test password."""
    return "TestPassword123!"


@pytest.fixture
def hashed_test_password(test_password: str) -> str:
    """Return a hashed version of the test password."""
    return get_password_hash(test_password)


def create_user_with_token(db_session: Session, test_password: str, **user_kwargs) -> Tuple[User, Dict[str, str]]:
    """Helper function to create a user and generate authentication headers.
    
    This should be used instead of calling /auth/login directly in tests.
    Only authentication tests should test the login endpoint directly.
    
    Args:
        db_session: The database session
        test_password: The plaintext password to use
        **user_kwargs: Additional user attributes (email, username, etc.)
        
    Returns:
        tuple: (user_object, auth_headers_dict)
    """
    
    # Create user with hashed password
    user = UserFactory.build(
        hashed_password=get_password_hash(test_password),
        **user_kwargs
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create token directly without calling the login endpoint
    token = create_access_token(data={"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    return user, headers


@pytest.fixture
def auth_headers(client: TestClient, db_session: Session, test_password: str) -> dict:
    """Create a test user and return authentication headers.
    
    This fixture is available to all test files for testing authenticated endpoints.
    """
    from tests.factories.user_factory import UserFactory
    
    # Create a user with known password
    user = UserFactory.build(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash(test_password),
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": test_password,
        },
    )
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

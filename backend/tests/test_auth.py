"""Tests for authentication endpoints and functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories.user_factory import UserFactory


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""
    
    def test_register_new_user(self, client: TestClient, db_session: Session):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(
        self, client: TestClient, db_session: Session
    ):
        """Test registration fails with duplicate email."""
        # Create an existing user
        existing_user = UserFactory.build(email="existing@example.com")
        db_session.add(existing_user)
        db_session.commit()
        
        # Try to register with the same email
        user_data = {
            "email": "existing@example.com",
            "username": "newuser",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
    
    def test_login_success(
        self, client: TestClient, db_session: Session, test_password: str
    ):
        """Test successful login returns access token."""
        from auth_utils import get_password_hash
        
        # Create a user with known password
        user = UserFactory.build(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash(test_password),
        )
        db_session.add(user)
        db_session.commit()
        
        # Login
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": test_password,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login fails with invalid credentials."""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401

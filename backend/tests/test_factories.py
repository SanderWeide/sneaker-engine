"""Tests for user model factories using Polyfactory."""
import pytest
from sqlalchemy.orm import Session

from tests.factories.user_factory import UserFactory
from models.user import User


class TestUserFactory:
    """Test suite for UserFactory."""
    
    def test_build_user(self):
        """Test building a user instance without persistence."""
        user = UserFactory.build()
        
        assert isinstance(user, User)
        assert user.email is not None
        assert user.username is not None
        assert user.first_name is not None
        assert user.last_name is not None
        assert user.hashed_password is not None
        assert "@" in user.email
    
    def test_build_with_custom_values(self):
        """Test building a user with custom values."""
        custom_email = "custom@example.com"
        custom_username = "customuser"
        
        user = UserFactory.build(
            email=custom_email,
            username=custom_username,
        )
        
        assert user.email == custom_email
        assert user.username == custom_username
    
    def test_batch_build(self):
        """Test building multiple users at once."""
        users = UserFactory.batch(5)
        
        assert len(users) == 5
        assert all(isinstance(user, User) for user in users)
        
        # Verify all emails are unique
        emails = [user.email for user in users]
        assert len(emails) == len(set(emails))
    
    def test_manual_persist_to_db(self, db_session: Session):
        """Test that factory-built users can be persisted to the database."""
        # Build a user and manually persist it
        user = UserFactory.build()
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify it was persisted
        db_user = db_session.query(User).filter_by(email=user.email).first()
        assert db_user is not None
        assert db_user.id == user.id
        assert db_user.email == user.email
    
    def test_factory_generates_valid_data(self):
        """Test that factory generates valid data for all fields."""
        user = UserFactory.build()
        
        # Check email format
        assert "@" in user.email
        assert "." in user.email
        
        # Check username is not empty
        assert len(user.username) > 0
        
        # Check names
        assert len(user.first_name) > 0
        assert len(user.last_name) > 0
        
        # Middle name can be None or a string
        if user.middle_name is not None:
            assert len(user.middle_name) > 0
        
        # Check password hash
        assert len(user.hashed_password) > 0
        assert user.hashed_password.startswith("$2b$")  # Should be bcrypt hashed

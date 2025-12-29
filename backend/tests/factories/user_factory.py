"""User model factory for generating test User instances."""
from datetime import datetime, timezone
from polyfactory import Use

from models.user import User
from .base import BaseFactory


class UserFactory(BaseFactory):
    """Factory for generating User model instances.
    
    Usage:
        # Generate a single user (not persisted)
        user = UserFactory.build()
        
        # Generate multiple users
        users = UserFactory.batch(5)
        
        # Generate with specific values
        user = UserFactory.build(email="test@example.com", username="testuser")
        
        # Persist to database
        user = UserFactory.create_sync(session=db_session)
    """
    
    __model__ = User
    
    # Custom field generation
    email = Use(lambda: UserFactory.__faker__.email())
    username = Use(lambda: UserFactory.__faker__.user_name())
    first_name = Use(lambda: UserFactory.__faker__.first_name())
    last_name = Use(lambda: UserFactory.__faker__.last_name())
    middle_name = Use(lambda: UserFactory.__faker__.first_name() if UserFactory.__random__.choice([True, False]) else None)
    hashed_password = Use(lambda: "$2b$12$KIX7jvHT3IgqN7tJZOQGnO7B7z8pV0z3X4BZqYxCpPsZqQBYZEF8e")  # "password123"
    created_at = Use(lambda: datetime.now(timezone.utc))
    updated_at = Use(lambda: None)

"""Tests for sneaker endpoints and functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth_utils import get_password_hash
from tests.factories.user_factory import UserFactory
from tests.factories.sneaker_factory import SneakerFactory


class TestSneakerEndpoints:
    """Test suite for sneaker endpoints."""
    
    def test_create_sneaker(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
    ):
        """Test creating a new sneaker."""
        sneaker_data = {
            "sku": "SKU-12345678",
            "brand": "Nike",
            "model": "Air Max 90",
            "size": 42.0,
            "color": "White/Black",
            "purchase_price": 120.00,
            "description": "Classic Air Max design",
        }
        
        response = client.post(
            "/api/sneakers",
            json=sneaker_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == sneaker_data["sku"]
        assert data["brand"] == sneaker_data["brand"]
        assert data["model"] == sneaker_data["model"]
        assert "id" in data
    
    def test_get_user_sneakers(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
    ):
        """Test retrieving user's sneakers."""
        # Get the current user
        user = db_session.query(UserFactory.__model__).filter_by(email="test@example.com").first()
        
        # Create some sneakers for the user
        sneakers = SneakerFactory.batch(3, user_id=user.id)
        for sneaker in sneakers:
            db_session.add(sneaker)
        db_session.commit()
        
        # Get the user's sneakers
        response = client.get("/api/sneakers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_get_sneaker_by_id(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
    ):
        """Test retrieving a specific sneaker by ID."""
        # Get the current user
        user = db_session.query(UserFactory.__model__).filter_by(email="test@example.com").first()
        
        # Create a sneaker
        sneaker = SneakerFactory.build(user_id=user.id)
        db_session.add(sneaker)
        db_session.commit()
        db_session.refresh(sneaker)
        
        # Get the sneaker
        response = client.get(f"/api/sneakers/{sneaker.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sneaker.id
        assert data["sku"] == sneaker.sku
    
    def test_update_sneaker(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
    ):
        """Test updating a sneaker."""
        # Get the current user
        user = db_session.query(UserFactory.__model__).filter_by(email="test@example.com").first()
        
        # Create a sneaker
        sneaker = SneakerFactory.build(user_id=user.id, purchase_price=100.0)
        db_session.add(sneaker)
        db_session.commit()
        db_session.refresh(sneaker)
        
        # Update the sneaker
        update_data = {"purchase_price": 150.0}
        response = client.put(
            f"/api/sneakers/{sneaker.id}",
            json=update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["purchase_price"] == 150.0
    
    def test_delete_sneaker(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
    ):
        """Test deleting a sneaker."""
        # Get the current user
        user = db_session.query(UserFactory.__model__).filter_by(email="test@example.com").first()
        
        # Create a sneaker
        sneaker = SneakerFactory.build(user_id=user.id)
        db_session.add(sneaker)
        db_session.commit()
        db_session.refresh(sneaker)
        
        # Delete the sneaker
        response = client.delete(
            f"/api/sneakers/{sneaker.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(f"/api/sneakers/{sneaker.id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_unauthorized_access(self, client: TestClient):
        """Test that create endpoint requires authentication."""
        sneaker_data = {
            "sku": "SKU-12345678",
            "brand": "Nike",
            "model": "Air Max 90",
            "size": 42.0,
            "color": "White/Black",
            "purchase_price": 120.00,
        }
        response = client.post("/api/sneakers", json=sneaker_data)
        assert response.status_code == 401
    
    def test_cannot_update_other_users_sneaker(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
        test_password: str,
    ):
        """Test that a user cannot update another user's sneaker."""
        # Get the first user (owner)
        owner = db_session.query(UserFactory.__model__).filter_by(email="test@example.com").first()
        
        # Create a sneaker for the owner
        sneaker = SneakerFactory.build(user_id=owner.id, purchase_price=100.0)
        db_session.add(sneaker)
        db_session.commit()
        db_session.refresh(sneaker)
        
        # Create a second user
        other_user = UserFactory.build(
            email="otheruser@example.com",
            username="otheruser",
            hashed_password=get_password_hash(test_password),
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Login as the second user
        response = client.post(
            "/auth/login",
            data={
                "username": "otheruser@example.com",
                "password": test_password,
            },
        )
        other_user_token = response.json()["access_token"]
        other_user_headers = {"Authorization": f"Bearer {other_user_token}"}
        
        # Try to update the owner's sneaker
        update_data = {"purchase_price": 150.0}
        response = client.put(
            f"/api/sneakers/{sneaker.id}",
            json=update_data,
            headers=other_user_headers,
        )
        
        # Should be forbidden (403) or not found (404)
        assert response.status_code in [403, 404]
    
    def test_cannot_delete_other_users_sneaker(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
        test_password: str,
    ):
        """Test that a user cannot delete another user's sneaker."""
        # Get the first user (owner)
        owner = db_session.query(UserFactory.__model__).filter_by(email="test@example.com").first()
        
        # Create a sneaker for the owner
        sneaker = SneakerFactory.build(user_id=owner.id)
        db_session.add(sneaker)
        db_session.commit()
        db_session.refresh(sneaker)
        
        # Create a second user
        other_user = UserFactory.build(
            email="otheruser@example.com",
            username="otheruser",
            hashed_password=get_password_hash(test_password),
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Login as the second user
        response = client.post(
            "/auth/login",
            data={
                "username": "otheruser@example.com",
                "password": test_password,
            },
        )
        other_user_token = response.json()["access_token"]
        other_user_headers = {"Authorization": f"Bearer {other_user_token}"}
        
        # Try to delete the owner's sneaker
        response = client.delete(
            f"/api/sneakers/{sneaker.id}",
            headers=other_user_headers,
        )
        
        # Should be forbidden (403) or not found (404)
        assert response.status_code in [403, 404]
        
        # Verify sneaker still exists by logging in as owner
        verify_response = client.get(
            f"/api/sneakers/{sneaker.id}",
            headers=auth_headers,
        )
        assert verify_response.status_code == 200

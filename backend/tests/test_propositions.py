"""Tests for proposition endpoints."""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories.user_factory import UserFactory
from tests.factories.sneaker_factory import SneakerFactory
from tests.factories.proposition_factory import PropositionFactory
from tests.conftest import create_user_with_token


@pytest.fixture
def seller_with_sneaker(db_session: Session, test_password: str):
    """Create a seller with authentication and a sneaker."""
    seller, seller_headers = create_user_with_token(db_session, test_password)
    sneaker = SneakerFactory.build(user_id=seller.id)
    db_session.add(sneaker)
    db_session.commit()
    return seller, seller_headers, sneaker


@pytest.fixture
def buyer_user(db_session: Session, test_password: str):
    """Create a buyer with authentication."""
    buyer, buyer_headers = create_user_with_token(db_session, test_password)
    return buyer, buyer_headers


@pytest.fixture
def proposition_with_users(db_session: Session, seller_with_sneaker, buyer_user):
    """Create a proposition with seller, buyer, and sneaker."""
    seller, seller_headers, sneaker = seller_with_sneaker
    buyer, buyer_headers = buyer_user
    
    proposition = PropositionFactory.build(seller_id=seller.id, buyer_id=buyer.id, sneaker_id=sneaker.id)
    db_session.add(proposition)
    db_session.commit()
    
    return proposition, seller, seller_headers, buyer, buyer_headers


class TestCreateProposition:
    """Tests for POST /api/propositions"""
    
    def test_seller_create_proposition_with_sneaker(self, client: TestClient, seller_with_sneaker, buyer_user):
        """Test creating a proposition with a sneaker reference"""
        seller, seller_headers, sneaker = seller_with_sneaker
        buyer, _ = buyer_user
        
        proposition_data = {
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "sneaker_id": sneaker.id,
            "value": 200.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=seller_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["seller_id"] == seller.id
        assert data["buyer_id"] == buyer.id
        assert data["value"] == 200.00
        assert data["sneaker_id"] == sneaker.id
        assert "id" in data
        assert "agreed_datetime" in data

    def test_buyer_create_proposition_with_sneaker(self, client: TestClient, seller_with_sneaker, buyer_user):
        """Test creating a proposition with a sneaker reference"""
        seller, _, sneaker = seller_with_sneaker
        buyer, buyer_headers = buyer_user
        
        proposition_data = {
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "sneaker_id": sneaker.id,
            "value": 150.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=buyer_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["seller_id"] == seller.id
        assert data["buyer_id"] == buyer.id
        assert data["value"] == 150.00
        assert data["sneaker_id"] == sneaker.id
        assert "id" in data
        assert "agreed_datetime" in data
    
    def test_create_proposition_not_involved(self, client: TestClient, db_session: Session, test_password: str, seller_with_sneaker, buyer_user):
        """Test that a user who is neither seller nor buyer cannot create proposition"""
        seller, _, sneaker = seller_with_sneaker
        buyer, _ = buyer_user
        _, outsider_headers = create_user_with_token(db_session, test_password)
        
        # Try to create proposition
        proposition_data = {
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "sneaker_id": sneaker.id,
            "value": 150.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=outsider_headers,
        )
        
        assert response.status_code == 403
        assert "seller or buyer" in response.json()["detail"].lower()
    
    def test_create_proposition_same_user(self, client: TestClient, db_session: Session, auth_headers: dict):
        """Test that seller and buyer must be different users"""
        # Get current user ID
        response = client.get("/api/users/me", headers=auth_headers)
        user_id = response.json()["id"]
        
        # Create a sneaker
        sneaker = SneakerFactory.build(user_id=user_id)
        db_session.add(sneaker)
        db_session.commit()
        
        # Try to create proposition with same user as seller and buyer
        proposition_data = {
            "seller_id": user_id,
            "buyer_id": user_id,
            "sneaker_id": sneaker.id,
            "value": 150.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 400
        assert "different" in response.json()["detail"].lower()
    
    def test_create_proposition_invalid_sneaker(self, client: TestClient, seller_with_sneaker, buyer_user):
        """Test creating proposition with non-existent sneaker"""
        seller, seller_headers, _ = seller_with_sneaker
        buyer, _ = buyer_user
        
        # Try to create proposition with invalid sneaker
        proposition_data = {
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "sneaker_id": 99999,
            "value": 150.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=seller_headers,
        )
        
        assert response.status_code == 404
        assert "sneaker" in response.json()["detail"].lower()


class TestOpenProposition:
    """Tests for POST /api/propositions with open propositions (no buyer)"""
    
    def test_create_open_proposition_success(self, client: TestClient, seller_with_sneaker):
        """Test creating an open proposition without a buyer"""
        seller, seller_headers, sneaker = seller_with_sneaker
        
        # Create open proposition (no buyer_id)
        proposition_data = {
            "seller_id": seller.id,
            "sneaker_id": sneaker.id,
            "value": 150.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=seller_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["seller_id"] == seller.id
        assert data["buyer_id"] is None
        assert data["sneaker_id"] == sneaker.id
        assert data["value"] == 150.00
    
    def test_create_open_proposition_not_seller(self, client: TestClient, db_session: Session, test_password: str, seller_with_sneaker):
        """Test that only the seller can create an open proposition"""
        seller, _, sneaker = seller_with_sneaker
        _, other_headers = create_user_with_token(db_session, test_password)
        
        # Try to create open proposition as non-seller
        proposition_data = {
            "seller_id": seller.id,
            "sneaker_id": sneaker.id,
            "value": 150.00,
        }
        
        response = client.post(
            "/api/propositions",
            json=proposition_data,
            headers=other_headers,
        )
        
        assert response.status_code == 403
        assert "open propositions as the seller" in response.json()["detail"].lower()
    
    def test_get_open_proposition_anyone(self, client: TestClient, db_session: Session, test_password: str, seller_with_sneaker):
        """Test that anyone can view an open proposition"""
        seller, _, sneaker = seller_with_sneaker
        _, random_headers = create_user_with_token(db_session, test_password)
        
        # Create open proposition
        proposition = PropositionFactory.build(seller_id=seller.id, buyer_id=None, sneaker_id=sneaker.id)
        db_session.add(proposition)
        db_session.commit()
        
        # Random user should be able to view open proposition
        response = client.get(f"/api/propositions/{proposition.id}", headers=random_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["buyer_id"] is None


class TestReadPropositions:
    """Tests for GET /api/propositions"""
    
    def test_get_all_propositions(self, client: TestClient, db_session: Session, seller_with_sneaker, buyer_user):
        """Test getting all propositions"""
        seller, seller_headers, sneaker = seller_with_sneaker
        buyer, _ = buyer_user
        
        propositions = PropositionFactory.batch(3, seller_id=seller.id, buyer_id=buyer.id, sneaker_id=sneaker.id)
        db_session.add_all(propositions)
        db_session.commit()
        
        # Get all propositions
        response = client.get("/api/propositions", headers=seller_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    def test_get_propositions_by_seller(self, client: TestClient, db_session: Session, test_password: str, buyer_user):
        """Test filtering propositions by seller_id"""
        # Create two sellers with sneakers
        seller1, seller1_headers = create_user_with_token(db_session, test_password)
        seller2, _ = create_user_with_token(db_session, test_password)
        buyer, _ = buyer_user
        
        # Create sneakers
        sneaker1 = SneakerFactory.build(user_id=seller1.id)
        sneaker2 = SneakerFactory.build(user_id=seller2.id)
        db_session.add_all([sneaker1, sneaker2])
        db_session.commit()
        
        # Create propositions
        props1 = PropositionFactory.batch(2, seller_id=seller1.id, buyer_id=buyer.id, sneaker_id=sneaker1.id)
        props2 = PropositionFactory.batch(3, seller_id=seller2.id, buyer_id=buyer.id, sneaker_id=sneaker2.id)
        db_session.add_all(props1 + props2)
        db_session.commit()
        
        # Filter by seller1
        response = client.get(
            f"/api/propositions?seller_id={seller1.id}",
            headers=seller1_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["seller_id"] == seller1.id for p in data)
    
    def test_get_my_propositions(self, client: TestClient, db_session: Session, test_password: str):
        """Test getting user's own propositions (as seller or buyer)"""
        # Create users
        user, user_headers = create_user_with_token(db_session, test_password)
        other_user1, _ = create_user_with_token(db_session, test_password)
        other_user2, _ = create_user_with_token(db_session, test_password)
        
        # Create sneakers
        sneaker1 = SneakerFactory.build(user_id=user.id)
        sneaker2 = SneakerFactory.build(user_id=other_user2.id)
        sneaker3 = SneakerFactory.build(user_id=other_user1.id)
        db_session.add_all([sneaker1, sneaker2, sneaker3])
        db_session.commit()
        
        # Create propositions where user is seller
        props_as_seller = PropositionFactory.batch(2, seller_id=user.id, buyer_id=other_user1.id, sneaker_id=sneaker1.id)
        # Create propositions where user is buyer
        props_as_buyer = PropositionFactory.batch(3, seller_id=other_user2.id, buyer_id=user.id, sneaker_id=sneaker2.id)
        # Create propositions not involving user
        other_props = PropositionFactory.batch(2, seller_id=other_user1.id, buyer_id=other_user2.id, sneaker_id=sneaker3.id)
        
        db_session.add_all(props_as_seller + props_as_buyer + other_props)
        db_session.commit()
        
        # Get user's propositions
        response = client.get("/api/propositions/my-propositions", headers=user_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # 2 as seller + 3 as buyer
        assert all(p["seller_id"] == user.id or p["buyer_id"] == user.id for p in data)


class TestReadProposition:
    """Tests for GET /api/propositions/{id}"""
    
    def test_get_proposition_as_seller(self, client: TestClient, proposition_with_users):
        """Test getting proposition details as seller"""
        proposition, seller, seller_headers, buyer, _ = proposition_with_users
        
        # Get proposition
        response = client.get(f"/api/propositions/{proposition.id}", headers=seller_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == proposition.id
        assert data["seller_id"] == seller.id
        assert data["buyer_id"] == buyer.id
    
    def test_get_proposition_unauthorized(self, client: TestClient, db_session: Session, test_password: str, proposition_with_users):
        """Test that outsider cannot access proposition"""
        proposition, _, _, _, _ = proposition_with_users
        _, outsider_headers = create_user_with_token(db_session, test_password)
        
        # Try to access proposition
        response = client.get(f"/api/propositions/{proposition.id}", headers=outsider_headers)
        
        assert response.status_code == 403
    
    def test_get_nonexistent_proposition(self, client: TestClient, auth_headers: dict):
        """Test getting a proposition that doesn't exist"""
        response = client.get("/api/propositions/99999", headers=auth_headers)
        
        assert response.status_code == 404


class TestUpdateProposition:
    """Tests for PUT /api/propositions/{id}"""
    
    def test_update_proposition_value(self, client: TestClient, proposition_with_users):
        """Test updating proposition value"""
        proposition, _, seller_headers, _, _ = proposition_with_users
        
        # Store original value
        original_value = proposition.value
        new_value = original_value + 100.00
        
        # Update proposition
        update_data = {"value": new_value}
        response = client.put(
            f"/api/propositions/{proposition.id}",
            json=update_data,
            headers=seller_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == new_value
        assert data["value"] != original_value
    
    def test_update_proposition_unauthorized(self, client: TestClient, db_session: Session, test_password: str, proposition_with_users):
        """Test that outsider cannot update proposition"""
        proposition, _, _, _, _ = proposition_with_users
        _, outsider_headers = create_user_with_token(db_session, test_password)
        
        # Try to update proposition
        update_data = {"value": 300.00}
        response = client.put(
            f"/api/propositions/{proposition.id}",
            json=update_data,
            headers=outsider_headers,
        )
        
        assert response.status_code == 403


class TestDeleteProposition:
    """Tests for DELETE /api/propositions/{id}"""
    
    def test_delete_proposition_as_seller(self, client: TestClient, proposition_with_users):
        """Test deleting proposition as seller"""
        proposition, _, seller_headers, _, _ = proposition_with_users
        proposition_id = proposition.id
        
        # Delete proposition
        response = client.delete(f"/api/propositions/{proposition_id}", headers=seller_headers)
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/api/propositions/{proposition_id}", headers=seller_headers)
        assert response.status_code == 404
    
    def test_delete_proposition_unauthorized(self, client: TestClient, db_session: Session, test_password: str, proposition_with_users):
        """Test that outsider cannot delete proposition"""
        proposition, _, _, _, _ = proposition_with_users
        _, outsider_headers = create_user_with_token(db_session, test_password)
        
        # Try to delete proposition
        response = client.delete(f"/api/propositions/{proposition.id}", headers=outsider_headers)
        
        assert response.status_code == 403

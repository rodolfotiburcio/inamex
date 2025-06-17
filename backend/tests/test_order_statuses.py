import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import OrderStatus
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def test_order_status():
    return {
        "name": "Test Status",
        "description": "Test Description",
        "order": 1,
        "active": True
    }

def test_create_order_status(test_order_status):
    response = client.post("/order-statuses/", json=test_order_status)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_order_status["name"]
    assert data["description"] == test_order_status["description"]
    assert data["order"] == test_order_status["order"]
    assert data["active"] == test_order_status["active"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_order_statuses():
    # Create a test order status
    test_status = OrderStatus(name="Test Status")
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)

    # Make the request to get all statuses
    response = client.get("/order-statuses/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(status["name"] == "Test Status" for status in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_status)
        session.commit()

def test_get_single_order_status():
    # Create a test order status
    test_status = OrderStatus(name="Single Test Status")
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)
        status_id = test_status.id

    # Make the request to get the specific status
    response = client.get(f"/order-statuses/{status_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test Status"
    assert data["id"] == status_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_status)
        session.commit()

def test_create_order_status():
    # Data for the new status
    new_status_data = {
        "name": "New Test Status",
        "description": "Test Description",
        "order": 1,
        "active": True
    }

    # Make the request to create a status
    response = client.post("/order-statuses/", json=new_status_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test Status"
    assert data["description"] == "Test Description"
    assert data["order"] == 1
    assert data["active"] == True
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(OrderStatus).where(OrderStatus.name == "New Test Status")
        test_status = session.exec(statement).first()
        if test_status:
            session.delete(test_status)
            session.commit()

def test_get_order_status():
    # First create a status to get
    test_status = {
        "name": "Test Get Status",
        "description": "Test Get Description",
        "order": 2,
        "active": True
    }
    create_response = client.post("/order-statuses/", json=test_status)
    assert create_response.status_code == 200
    status_id = create_response.json()["id"]

    # Now get it
    response = client.get(f"/order-statuses/{status_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == status_id
    assert data["name"] == test_status["name"]
    assert data["description"] == test_status["description"]
    assert data["order"] == test_status["order"]
    assert data["active"] == test_status["active"]

def test_update_order_status():
    """Test updating an order status"""
    # Create a test status
    test_status = OrderStatus(
        name="Original Status",
        description="Original Description",
        order=1,
        active=True
    )
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)
        status_id = test_status.id
        original_created_at = test_status.created_at
    
    # Update the status
    response = client.put(
        f"/order-statuses/{status_id}",
        json={
            "name": "Updated Status",
            "description": "Updated Description",
            "order": 2,
            "active": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == status_id
    assert data["name"] == "Updated Status"
    assert data["description"] == "Updated Description"
    assert data["order"] == 2
    assert data["active"] == False
    assert data["created_at"] == original_created_at.isoformat()
    assert data["updated_at"] != original_created_at.isoformat()
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_status = session.get(OrderStatus, status_id)
        assert updated_status.name == "Updated Status"
        assert updated_status.description == "Updated Description"
        assert updated_status.order == 2
        assert updated_status.active == False
        assert updated_status.created_at == original_created_at
        assert updated_status.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_status)
        session.commit()

def test_update_order_status_partial():
    """Test updating only some fields of an order status"""
    # Create a test status
    test_status = OrderStatus(
        name="Partial Update Status",
        description="Original Description",
        order=1,
        active=True
    )
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)
        status_id = test_status.id
        original_created_at = test_status.created_at
    
    # Update only the name
    response = client.put(
        f"/order-statuses/{status_id}",
        json={
            "name": "Partially Updated Status"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == status_id
    assert data["name"] == "Partially Updated Status"
    assert data["description"] == "Original Description"  # Should not change
    assert data["order"] == 1  # Should not change
    assert data["active"] == True  # Should not change
    assert data["created_at"] == original_created_at.isoformat()
    assert data["updated_at"] != original_created_at.isoformat()
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_status = session.get(OrderStatus, status_id)
        assert updated_status.name == "Partially Updated Status"
        assert updated_status.description == "Original Description"
        assert updated_status.order == 1
        assert updated_status.active == True
        assert updated_status.created_at == original_created_at
        assert updated_status.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_status)
        session.commit()

def test_update_order_status_not_found():
    """Test updating a non-existent order status"""
    response = client.put(
        "/order-statuses/999999",  # ID that surely doesn't exist
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Order status not found" in response.json()["detail"]

def test_delete_order_status():
    # Create a test order status
    test_status = OrderStatus(name="Status To Delete")
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)
        status_id = test_status.id

    # Make the request to delete the status
    response = client.delete(f"/order-statuses/{status_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Order status deleted"

    # Verify the status was actually deleted
    with Session(engine) as session:
        statement = select(OrderStatus).where(OrderStatus.id == status_id)
        deleted_status = session.exec(statement).first()
        assert deleted_status is None

def test_get_nonexistent_order_status():
    response = client.get("/order-statuses/999999")
    assert response.status_code == 404 
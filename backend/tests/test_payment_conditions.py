from fastapi.testclient import TestClient
from app.main import app
from app.models import PaymentCondition
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime

client = TestClient(app)

def test_get_payment_conditions():
    # Create a test payment condition
    test_condition = PaymentCondition(
        name="Test Condition",
        text="Test Text",
        description="Test Description",
        active=True
    )
    with Session(engine) as session:
        session.add(test_condition)
        session.commit()
        session.refresh(test_condition)

    # Make the request to get all conditions
    response = client.get("/payment-conditions/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(condition["name"] == "Test Condition" for condition in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_condition)
        session.commit()

def test_get_single_payment_condition():
    # Create a test payment condition
    test_condition = PaymentCondition(
        name="Single Test Condition",
        text="Single Test Text",
        description="Single Test Description",
        active=True
    )
    with Session(engine) as session:
        session.add(test_condition)
        session.commit()
        session.refresh(test_condition)
        condition_id = test_condition.id

    # Make the request to get the specific condition
    response = client.get(f"/payment-conditions/{condition_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test Condition"
    assert data["text"] == "Single Test Text"
    assert data["description"] == "Single Test Description"
    assert data["active"] == True
    assert data["id"] == condition_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_condition)
        session.commit()

def test_create_payment_condition():
    # Data for the new condition
    new_condition_data = {
        "name": "New Test Condition",
        "text": "New Test Text",
        "description": "New Test Description",
        "active": True
    }

    # Make the request to create a condition
    response = client.post("/payment-conditions/", json=new_condition_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test Condition"
    assert data["text"] == "New Test Text"
    assert data["description"] == "New Test Description"
    assert data["active"] == True
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(PaymentCondition).where(PaymentCondition.name == "New Test Condition")
        test_condition = session.exec(statement).first()
        if test_condition:
            session.delete(test_condition)
            session.commit()

def test_delete_payment_condition():
    # Create a test payment condition
    test_condition = PaymentCondition(
        name="Condition To Delete",
        text="Delete Test Text",
        description="Delete Test Description",
        active=True
    )
    with Session(engine) as session:
        session.add(test_condition)
        session.commit()
        session.refresh(test_condition)
        condition_id = test_condition.id

    # Make the request to delete the condition
    response = client.delete(f"/payment-conditions/{condition_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Payment condition deleted"

    # Verify the condition was actually deleted
    with Session(engine) as session:
        statement = select(PaymentCondition).where(PaymentCondition.id == condition_id)
        deleted_condition = session.exec(statement).first()
        assert deleted_condition is None

def test_update_payment_condition():
    """Test updating a payment condition"""
    # Create a test condition
    test_condition = PaymentCondition(
        name="Original Condition",
        text="Original Text",
        description="Original Description",
        active=True
    )
    with Session(engine) as session:
        session.add(test_condition)
        session.commit()
        session.refresh(test_condition)
        condition_id = test_condition.id
        original_created_at = test_condition.created_at
    
    # Update the condition
    response = client.put(
        f"/payment-conditions/{condition_id}",
        json={
            "name": "Updated Condition",
            "text": "Updated Text",
            "description": "Updated Description",
            "active": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == condition_id
    assert data["name"] == "Updated Condition"
    assert data["text"] == "Updated Text"
    assert data["description"] == "Updated Description"
    assert data["active"] == False
    assert data["created_at"] == original_created_at.isoformat()
    assert data["updated_at"] != original_created_at.isoformat()
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_condition = session.get(PaymentCondition, condition_id)
        assert updated_condition.name == "Updated Condition"
        assert updated_condition.text == "Updated Text"
        assert updated_condition.description == "Updated Description"
        assert updated_condition.active == False
        assert updated_condition.created_at == original_created_at
        assert updated_condition.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_condition)
        session.commit()

def test_update_payment_condition_partial():
    """Test updating only some fields of a payment condition"""
    # Create a test condition
    test_condition = PaymentCondition(
        name="Partial Update Condition",
        text="Original Text",
        description="Original Description",
        active=True
    )
    with Session(engine) as session:
        session.add(test_condition)
        session.commit()
        session.refresh(test_condition)
        condition_id = test_condition.id
        original_created_at = test_condition.created_at
    
    # Update only the name
    response = client.put(
        f"/payment-conditions/{condition_id}",
        json={
            "name": "Partially Updated Condition"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == condition_id
    assert data["name"] == "Partially Updated Condition"
    assert data["text"] == "Original Text"  # Should not change
    assert data["description"] == "Original Description"  # Should not change
    assert data["active"] == True  # Should not change
    assert data["created_at"] == original_created_at.isoformat()
    assert data["updated_at"] != original_created_at.isoformat()
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_condition = session.get(PaymentCondition, condition_id)
        assert updated_condition.name == "Partially Updated Condition"
        assert updated_condition.text == "Original Text"
        assert updated_condition.description == "Original Description"
        assert updated_condition.active == True
        assert updated_condition.created_at == original_created_at
        assert updated_condition.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_condition)
        session.commit()

def test_update_payment_condition_not_found():
    """Test updating a non-existent payment condition"""
    response = client.put(
        "/payment-conditions/999999",  # ID that surely doesn't exist
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Payment condition not found" in response.json()["detail"] 
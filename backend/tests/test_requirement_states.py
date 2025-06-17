from fastapi.testclient import TestClient
from app.main import app
from app.models import RequirementState
from app.core.database import engine
from sqlmodel import Session, select

client = TestClient(app)

def test_get_requirement_states():
    # Create a test requirement state
    test_state = RequirementState(name="Test State")
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)

    # Make the request to get all states
    response = client.get("/requirement-states/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(state["name"] == "Test State" for state in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_state)
        session.commit()

def test_get_single_requirement_state():
    # Create a test requirement state
    test_state = RequirementState(name="Single Test State")
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)
        state_id = test_state.id

    # Make the request to get the specific state
    response = client.get(f"/requirement-states/{state_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test State"
    assert data["id"] == state_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_state)
        session.commit()

def test_create_requirement_state():
    # Data for the new state
    new_state_data = {
        "name": "New Test State",
        "description": "Test Description",
        "order": 1,
        "active": True
    }

    # Make the request to create a state
    response = client.post("/requirement-states/", json=new_state_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test State"
    assert data["description"] == "Test Description"
    assert data["order"] == 1
    assert data["active"] == True
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(RequirementState).where(RequirementState.name == "New Test State")
        test_state = session.exec(statement).first()
        if test_state:
            session.delete(test_state)
            session.commit()

def test_delete_requirement_state():
    # Create a test requirement state
    test_state = RequirementState(name="State To Delete")
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)
        state_id = test_state.id

    # Make the request to delete the state
    response = client.delete(f"/requirement-states/{state_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Requirement state deleted"

    # Verify the state was actually deleted
    with Session(engine) as session:
        statement = select(RequirementState).where(RequirementState.id == state_id)
        deleted_state = session.exec(statement).first()
        assert deleted_state is None

def test_update_requirement_state():
    """Test updating a requirement state"""
    # Create a test state
    test_state = RequirementState(
        name="Original State",
        description="Original Description",
        order=1,
        active=True
    )
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)
        state_id = test_state.id
        original_created_at = test_state.created_at
    
    # Update the state
    response = client.put(
        f"/requirement-states/{state_id}",
        json={
            "name": "Updated State",
            "description": "Updated Description",
            "order": 2,
            "active": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state_id
    assert data["name"] == "Updated State"
    assert data["description"] == "Updated Description"
    assert data["order"] == 2
    assert data["active"] == False
    assert data["created_at"] == original_created_at.isoformat()
    assert data["updated_at"] != original_created_at.isoformat()
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_state = session.get(RequirementState, state_id)
        assert updated_state.name == "Updated State"
        assert updated_state.description == "Updated Description"
        assert updated_state.order == 2
        assert updated_state.active == False
        assert updated_state.created_at == original_created_at
        assert updated_state.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_state)
        session.commit()

def test_update_requirement_state_partial():
    """Test updating only some fields of a requirement state"""
    # Create a test state
    test_state = RequirementState(
        name="Partial Update State",
        description="Original Description",
        order=1,
        active=True
    )
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)
        state_id = test_state.id
        original_created_at = test_state.created_at
    
    # Update only the name
    response = client.put(
        f"/requirement-states/{state_id}",
        json={
            "name": "Partially Updated State"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state_id
    assert data["name"] == "Partially Updated State"
    assert data["description"] == "Original Description"  # Should not change
    assert data["order"] == 1  # Should not change
    assert data["active"] == True  # Should not change
    assert data["created_at"] == original_created_at.isoformat()
    assert data["updated_at"] != original_created_at.isoformat()
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_state = session.get(RequirementState, state_id)
        assert updated_state.name == "Partially Updated State"
        assert updated_state.description == "Original Description"
        assert updated_state.order == 1
        assert updated_state.active == True
        assert updated_state.created_at == original_created_at
        assert updated_state.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_state)
        session.commit()

def test_update_requirement_state_not_found():
    """Test updating a non-existent requirement state"""
    response = client.put(
        "/requirement-states/999999",  # ID that surely doesn't exist
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Requirement state not found" in response.json()["detail"] 
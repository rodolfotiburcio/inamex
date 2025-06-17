from fastapi.testclient import TestClient
from app.main import app
from app.models import ProjectState
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime

client = TestClient(app)

def test_get_project_states():
    # Create a test project state
    test_state = ProjectState(name="Test State")
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)

    # Make the request to get all states
    response = client.get("/project-states/")
    
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

def test_get_single_project_state():
    # Create a test project state
    test_state = ProjectState(name="Single Test State")
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)
        state_id = test_state.id

    # Make the request to get the specific state
    response = client.get(f"/project-states/{state_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test State"
    assert data["id"] == state_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_state)
        session.commit()

def test_create_project_state():
    # Data for the new state
    new_state_data = {
        "name": "New Test State"
    }

    # Make the request to create a state
    response = client.post("/project-states/", json=new_state_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test State"
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(ProjectState).where(ProjectState.name == "New Test State")
        test_state = session.exec(statement).first()
        if test_state:
            session.delete(test_state)
            session.commit()

def test_delete_project_state():
    # Create a test project state
    test_state = ProjectState(name="State To Delete")
    with Session(engine) as session:
        session.add(test_state)
        session.commit()
        session.refresh(test_state)
        state_id = test_state.id

    # Make the request to delete the state
    response = client.delete(f"/project-states/{state_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Project state deleted"

    # Verify the state was actually deleted
    with Session(engine) as session:
        statement = select(ProjectState).where(ProjectState.id == state_id)
        deleted_state = session.exec(statement).first()
        assert deleted_state is None

def test_update_project_state():
    """Test updating a project state"""
    # Create a test state
    test_state = ProjectState(
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
        f"/project-states/{state_id}",
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
    assert data["active"] is False
    # Verificar que el created_at no cambia
    assert datetime.fromisoformat(data["created_at"]) == original_created_at
    # Verificar que el updated_at sí cambia
    assert datetime.fromisoformat(data["updated_at"]) > original_created_at
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_state = session.get(ProjectState, state_id)
        assert updated_state.name == "Updated State"
        assert updated_state.description == "Updated Description"
        assert updated_state.order == 2
        assert updated_state.active is False
        assert updated_state.created_at == original_created_at
        assert updated_state.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_state)
        session.commit()

def test_update_project_state_partial():
    """Test updating only some fields of a project state"""
    # Create a test state
    test_state = ProjectState(
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
    
    # Update only the name and order
    response = client.put(
        f"/project-states/{state_id}",
        json={
            "name": "Partially Updated State",
            "order": 3
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == state_id
    assert data["name"] == "Partially Updated State"
    assert data["description"] == "Original Description"  # No debería cambiar
    assert data["order"] == 3
    assert data["active"] is True  # No debería cambiar
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_state = session.get(ProjectState, state_id)
        assert updated_state.name == "Partially Updated State"
        assert updated_state.description == "Original Description"
        assert updated_state.order == 3
        assert updated_state.active is True
        
        # Cleanup
        session.delete(updated_state)
        session.commit()

def test_update_project_state_duplicate_name():
    """Test that updating a project state with an existing name fails"""
    # Create two states
    state1 = ProjectState(name="State One")
    state2 = ProjectState(name="State Two")
    with Session(engine) as session:
        session.add(state1)
        session.add(state2)
        session.commit()
        session.refresh(state1)
        session.refresh(state2)
        state1_id = state1.id
        state2_id = state2.id
    
    # Try to update state2 with the name of state1
    response = client.put(
        f"/project-states/{state2_id}",
        json={
            "name": "State One"
        }
    )
    
    assert response.status_code == 400
    assert "Project state name already exists" in response.json()["detail"]
    
    # Verify it didn't change
    with Session(engine) as session:
        unchanged_state = session.get(ProjectState, state2_id)
        assert unchanged_state.name == "State Two"
        
        # Cleanup
        session.delete(session.get(ProjectState, state1_id))
        session.delete(unchanged_state)
        session.commit()

def test_update_project_state_not_found():
    """Test updating a non-existent project state"""
    response = client.put(
        "/project-states/999999",  # ID que seguramente no existe
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Project state not found" in response.json()["detail"] 
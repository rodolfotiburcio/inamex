from fastapi.testclient import TestClient
from app.main import app
from app.models import Project, User, Client, ProjectState
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime

client = TestClient(app)

def create_test_dependencies():
    """Helper function to create required related entities"""
    with Session(engine) as session:
        # Create test user
        test_user = User(
            username="testuser",
            full_name="Test User",
            password_hash="hashedpassword123"
        )
        session.add(test_user)
        
        # Create test client
        test_client = Client(name="Test Client")
        session.add(test_client)
        
        # Create test state
        test_state = ProjectState(name="Test State")
        session.add(test_state)
        
        session.commit()
        session.refresh(test_user)
        session.refresh(test_client)
        session.refresh(test_state)
        
        return test_user.id, test_client.id, test_state.id

def cleanup_test_dependencies(user_id, client_id, state_id):
    """Helper function to clean up related entities"""
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
        
        client_obj = session.get(Client, client_id)
        if client_obj:
            session.delete(client_obj)
            
        state = session.get(ProjectState, state_id)
        if state:
            session.delete(state)
            
        session.commit()

def test_get_projects():
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create a test project
    test_project = Project(
        number="TEST-001",
        name="Test Project",
        client_id=client_id,
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_project)
        session.commit()
        session.refresh(test_project)

    # Make the request to get all projects
    response = client.get("/projects/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(project["name"] == "Test Project" for project in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_project)
        session.commit()
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_get_single_project():
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create a test project
    test_project = Project(
        number="TEST-002",
        name="Single Test Project",
        client_id=client_id,
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_project)
        session.commit()
        session.refresh(test_project)
        project_id = test_project.id

    # Make the request to get the specific project
    response = client.get(f"/projects/{project_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test Project"
    assert data["id"] == project_id
    assert data["client_id"] == client_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_project)
        session.commit()
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_create_project():
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Data for the new project
    new_project_data = {
        "number": "TEST-003",
        "name": "New Test Project",
        "client_id": client_id,
        "state_id": state_id,
        "description": "Test Description"
    }

    # Make the request to create a project
    response = client.post("/projects/", json=new_project_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test Project"
    assert data["client_id"] == client_id
    assert data["description"] == "Test Description"
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(Project).where(Project.name == "New Test Project")
        test_project = session.exec(statement).first()
        if test_project:
            session.delete(test_project)
        session.commit()
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_delete_project():
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create a test project
    test_project = Project(
        number="TEST-004",
        name="Project to Delete",
        client_id=client_id,
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_project)
        session.commit()
        session.refresh(test_project)
        project_id = test_project.id

    # Make the request to delete the project
    response = client.delete(f"/projects/{project_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Project deleted"

    # Verify the project was actually deleted
    with Session(engine) as session:
        statement = select(Project).where(Project.id == project_id)
        deleted_project = session.exec(statement).first()
        assert deleted_project is None

    # Clean up
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_create_project_invalid_references():
    """Test creating a project with invalid foreign keys"""
    # Try to create a project with non-existent references
    new_project_data = {
        "number": "TEST-005",
        "name": "Invalid Project",
        "description": "Invalid Project Description",
        "responsible_id": 99999,  # Non-existent user
        "client_id": 99999,      # Non-existent client
        "state_id": 99999        # Non-existent state
    }

    # Make the request to create a project
    response = client.post("/projects/", json=new_project_data)
    
    # Verify the response indicates an error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data  # Should contain error message 

def test_update_project():
    """Test updating a project"""
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create a second state for updating
    new_state = None
    with Session(engine) as session:
        new_state = ProjectState(name="Updated State")
        session.add(new_state)
        session.commit()
        session.refresh(new_state)
        new_state_id = new_state.id
    
    # Create a test project
    test_project = Project(
        number="TEST-006",
        name="Original Project Name",
        description="Original Description",
        state_id=state_id,
        client_id=client_id
    )
    with Session(engine) as session:
        session.add(test_project)
        session.commit()
        session.refresh(test_project)
        project_id = test_project.id
        original_date = test_project.date
    
    # Update the project
    response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Updated Project Name",
            "description": "Updated Description",
            "state_id": new_state_id
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Updated Project Name"
    assert data["description"] == "Updated Description"
    assert data["state_id"] == new_state_id
    assert data["number"] == "TEST-006"  # No debería cambiar
    assert data["client_id"] == client_id  # No debería cambiar
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_project = session.get(Project, project_id)
        assert updated_project.name == "Updated Project Name"
        assert updated_project.description == "Updated Description"
        assert updated_project.state_id == new_state_id
        assert updated_project.number == "TEST-006"
        assert updated_project.client_id == client_id
        assert updated_project.date == original_date
        
        # Cleanup
        session.delete(updated_project)
        session.delete(new_state)
        session.commit()
    
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_update_project_partial():
    """Test updating only some fields of a project"""
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create a test project
    test_project = Project(
        number="TEST-007",
        name="Partial Update Project",
        description="Original Description",
        state_id=state_id,
        client_id=client_id
    )
    with Session(engine) as session:
        session.add(test_project)
        session.commit()
        session.refresh(test_project)
        project_id = test_project.id
    
    # Update only the name
    response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Partially Updated Project"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Partially Updated Project"
    assert data["description"] == "Original Description"  # No debería cambiar
    assert data["state_id"] == state_id  # No debería cambiar
    assert data["client_id"] == client_id  # No debería cambiar
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_project = session.get(Project, project_id)
        assert updated_project.name == "Partially Updated Project"
        assert updated_project.description == "Original Description"
        assert updated_project.state_id == state_id
        assert updated_project.client_id == client_id
        
        # Cleanup
        session.delete(updated_project)
        session.commit()
    
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_update_project_duplicate_number():
    """Test that updating a project with an existing number fails"""
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create two projects
    project1 = Project(
        number="PROJ-001",
        name="Project One",
        state_id=state_id
    )
    project2 = Project(
        number="PROJ-002",
        name="Project Two",
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(project1)
        session.add(project2)
        session.commit()
        session.refresh(project1)
        session.refresh(project2)
        project1_id = project1.id
        project2_id = project2.id
    
    # Try to update project2 with the number of project1
    response = client.put(
        f"/projects/{project2_id}",
        json={
            "number": "PROJ-001"
        }
    )
    
    assert response.status_code == 400
    assert "Project number already exists" in response.json()["detail"]
    
    # Verify it didn't change
    with Session(engine) as session:
        unchanged_project = session.get(Project, project2_id)
        assert unchanged_project.number == "PROJ-002"
        
        # Cleanup
        session.delete(session.get(Project, project1_id))
        session.delete(unchanged_project)
        session.commit()
    
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_update_project_invalid_references():
    """Test updating a project with invalid foreign keys"""
    # Create test dependencies
    user_id, client_id, state_id = create_test_dependencies()
    
    # Create a test project
    test_project = Project(
        number="TEST-008",
        name="Invalid Reference Project",
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_project)
        session.commit()
        session.refresh(test_project)
        project_id = test_project.id
    
    # Try to update with non-existent references
    response = client.put(
        f"/projects/{project_id}",
        json={
            "state_id": 99999  # Non-existent state
        }
    )
    
    assert response.status_code == 400
    assert "Invalid state_id" in response.json()["detail"]
    
    # Verify it didn't change
    with Session(engine) as session:
        unchanged_project = session.get(Project, project_id)
        assert unchanged_project.state_id == state_id
        
        # Cleanup
        session.delete(unchanged_project)
        session.commit()
    
    cleanup_test_dependencies(user_id, client_id, state_id)

def test_update_project_not_found():
    """Test updating a non-existent project"""
    response = client.put(
        "/projects/999999",  # ID que seguramente no existe
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"] 
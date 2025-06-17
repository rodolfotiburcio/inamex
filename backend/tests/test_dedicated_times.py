from fastapi.testclient import TestClient
from app.main import app
from app.models import DedicatedTime, User, Report, Project, ProjectState, Client
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime, timedelta

client = TestClient(app)

def create_test_dependencies():
    """Helper function to create required related entities"""
    with Session(engine) as session:
        # Create test client
        test_client = Client(name="Test Client")
        session.add(test_client)
        session.commit()
        session.refresh(test_client)
        
        # Create test project state
        test_project_state = ProjectState(
            name="Test State",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_project_state)
        session.commit()
        session.refresh(test_project_state)
        
        # Create test user
        test_user = User(
            username="testuser",
            full_name="Test User",
            password_hash="hashedpassword123"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        
        # Create test project
        test_project = Project(
            number="TEST-001",
            name="Test Project",
            description="Test Description",
            state_id=test_project_state.id,
            responsible_id=test_user.id,
            client_id=test_client.id
        )
        session.add(test_project)
        session.commit()
        session.refresh(test_project)
        
        # Create test report
        test_report = Report(
            title="Test Report",
            description="Test Description",
            duration=timedelta(hours=2),
            dead_time=timedelta(minutes=30),
            project_id=test_project.id,
            responsible_id=test_user.id
        )
        session.add(test_report)
        session.commit()
        session.refresh(test_report)
        
        return test_user.id, test_report.id, test_project.id, test_project_state.id, test_client.id

def cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id):
    """Helper function to clean up related entities"""
    with Session(engine) as session:
        # Delete report
        report = session.get(Report, report_id)
        if report:
            session.delete(report)
            
        # Delete project
        project = session.get(Project, project_id)
        if project:
            session.delete(project)
            
        # Delete user
        user = session.get(User, user_id)
        if user:
            session.delete(user)
        
        # Delete project state
        state = session.get(ProjectState, state_id)
        if state:
            session.delete(state)
            
        # Delete client
        client_obj = session.get(Client, client_id)
        if client_obj:
            session.delete(client_obj)
            
        session.commit()

def test_get_dedicated_times():
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test dedicated time
    test_dedicated_time = DedicatedTime(
        user_id=user_id,
        time=timedelta(hours=1, minutes=30),
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_dedicated_time)
        session.commit()
        session.refresh(test_dedicated_time)

    # Make the request to get all dedicated times
    response = client.get("/dedicated-times/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(dt["user_id"] == user_id and dt["report_id"] == report_id for dt in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_dedicated_time)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_get_single_dedicated_time():
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test dedicated time
    test_dedicated_time = DedicatedTime(
        user_id=user_id,
        time=timedelta(hours=1, minutes=30),
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_dedicated_time)
        session.commit()
        session.refresh(test_dedicated_time)
        dedicated_time_id = test_dedicated_time.id

    # Make the request to get the specific dedicated time
    response = client.get(f"/dedicated-times/{dedicated_time_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["report_id"] == report_id
    assert "time" in data
    assert data["id"] == dedicated_time_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_dedicated_time)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_create_dedicated_time():
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Data for the new dedicated time
    new_dedicated_time_data = {
        "user_id": user_id,
        "time": "01:30:00",  # 1 hour 30 minutes
        "report_id": report_id
    }

    # Make the request to create a dedicated time
    response = client.post("/dedicated-times/", json=new_dedicated_time_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["report_id"] == report_id
    assert "time" in data
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(DedicatedTime).where(
            DedicatedTime.user_id == user_id,
            DedicatedTime.report_id == report_id
        )
        test_dedicated_time = session.exec(statement).first()
        if test_dedicated_time:
            session.delete(test_dedicated_time)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_delete_dedicated_time():
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test dedicated time
    test_dedicated_time = DedicatedTime(
        user_id=user_id,
        time=timedelta(hours=1, minutes=30),
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_dedicated_time)
        session.commit()
        session.refresh(test_dedicated_time)
        dedicated_time_id = test_dedicated_time.id

    # Make the request to delete the dedicated time
    response = client.delete(f"/dedicated-times/{dedicated_time_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Dedicated time deleted"

    # Verify the dedicated time was actually deleted
    with Session(engine) as session:
        statement = select(DedicatedTime).where(DedicatedTime.id == dedicated_time_id)
        deleted_dedicated_time = session.exec(statement).first()
        assert deleted_dedicated_time is None

    # Clean up
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_create_dedicated_time_invalid_references():
    """Test creating a dedicated time with invalid foreign keys"""
    # Try to create a dedicated time with non-existent references
    new_dedicated_time_data = {
        "user_id": 99999,      # Non-existent user
        "time": "01:30:00",    # 1 hour 30 minutes
        "report_id": 99999     # Non-existent report
    }

    # Make the request to create a dedicated time
    response = client.post("/dedicated-times/", json=new_dedicated_time_data)
    
    # Verify the response indicates an error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data  # Should contain error message

def test_get_nonexistent_dedicated_time():
    """Test getting a dedicated time that doesn't exist"""
    response = client.get("/dedicated-times/99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_delete_nonexistent_dedicated_time():
    """Test deleting a dedicated time that doesn't exist"""
    response = client.delete("/dedicated-times/99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_update_dedicated_time():
    """Test updating a dedicated time with valid data"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test dedicated time
    test_dedicated_time = DedicatedTime(
        user_id=user_id,
        time=timedelta(hours=1, minutes=30),
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_dedicated_time)
        session.commit()
        session.refresh(test_dedicated_time)
        dedicated_time_id = test_dedicated_time.id

    # Data for updating the dedicated time
    update_data = {
        "time": "PT2H",  # 2 hours in ISO 8601 format
        "user_id": user_id,
        "report_id": report_id
    }

    # Make the request to update the dedicated time
    response = client.put(f"/dedicated-times/{dedicated_time_id}", json=update_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dedicated_time_id
    assert data["time"] == "PT2H"
    assert data["user_id"] == user_id
    assert data["report_id"] == report_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_dedicated_time)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_update_dedicated_time_not_found():
    """Test updating a non-existent dedicated time"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Data for updating the dedicated time
    update_data = {
        "time": "PT2H",
        "user_id": user_id,
        "report_id": report_id
    }

    # Make the request to update a non-existent dedicated time
    response = client.put("/dedicated-times/999999", json=update_data)
    
    # Verify the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

    # Clean up
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_update_dedicated_time_invalid_references():
    """Test updating a dedicated time with invalid foreign keys"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test dedicated time
    test_dedicated_time = DedicatedTime(
        user_id=user_id,
        time=timedelta(hours=1, minutes=30),
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_dedicated_time)
        session.commit()
        session.refresh(test_dedicated_time)
        dedicated_time_id = test_dedicated_time.id

    # Data for updating the dedicated time with invalid references
    update_data = {
        "time": "PT2H",
        "user_id": 99999,      # Non-existent user
        "report_id": 99999     # Non-existent report
    }

    # Make the request to update the dedicated time
    response = client.put(f"/dedicated-times/{dedicated_time_id}", json=update_data)
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower()

    # Clean up
    with Session(engine) as session:
        session.delete(test_dedicated_time)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_update_dedicated_time_partial():
    """Test updating a dedicated time with partial data"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test dedicated time
    test_dedicated_time = DedicatedTime(
        user_id=user_id,
        time=timedelta(hours=1, minutes=30),
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_dedicated_time)
        session.commit()
        session.refresh(test_dedicated_time)
        dedicated_time_id = test_dedicated_time.id

    # Data for partial update
    update_data = {
        "time": "PT2H"  # Only update the time
    }

    # Make the request to update the dedicated time
    response = client.put(f"/dedicated-times/{dedicated_time_id}", json=update_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dedicated_time_id
    assert data["time"] == "PT2H"
    assert data["user_id"] == user_id  # Should remain unchanged
    assert data["report_id"] == report_id  # Should remain unchanged

    # Clean up
    with Session(engine) as session:
        session.delete(test_dedicated_time)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id) 
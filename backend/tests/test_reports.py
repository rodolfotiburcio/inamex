from fastapi.testclient import TestClient
from app.main import app
from app.models import Report, User, Project, ProjectState, Client
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
        
        # Create test user with unique username
        test_user = User(
            username=f"testuser_{datetime.utcnow().timestamp()}",
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
        
        return test_user.id, test_project.id, test_project_state.id, test_client.id

def cleanup_test_dependencies(user_id, project_id, state_id, client_id):
    """Helper function to clean up related entities"""
    with Session(engine) as session:
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

def test_get_reports():
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test report
    test_report = Report(
        title="Test Report",
        description="Test Description",
        duration=timedelta(hours=2),
        dead_time=timedelta(minutes=30),
        project_id=project_id,
        responsible_id=user_id
    )
    with Session(engine) as session:
        session.add(test_report)
        session.commit()
        session.refresh(test_report)

    # Make the request to get all reports
    response = client.get("/reports/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(report["title"] == "Test Report" for report in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_report)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)


def test_get_single_report():
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test report
    test_report = Report(
        title="Single Test Report",
        description="Test Description",
        duration=timedelta(hours=2),
        dead_time=timedelta(minutes=30),
        project_id=project_id,
        responsible_id=user_id
    )
    with Session(engine) as session:
        session.add(test_report)
        session.commit()
        session.refresh(test_report)
        report_id = test_report.id

    # Make the request to get the specific report
    response = client.get(f"/reports/{report_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Test Report"
    assert data["id"] == report_id
    assert data["project_id"] == project_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_report)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_create_report():
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Data for the new report
    new_report_data = {
        "title": "New Test Report",
        "description": "Test Description",
        "duration": "02:00:00",  # 2 hours
        "dead_time": "00:30:00",  # 30 minutes
        "project_id": project_id,
        "responsible_id": user_id
    }

    # Make the request to create a report
    response = client.post("/reports/", json=new_report_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Test Report"
    assert data["project_id"] == project_id
    assert data["description"] == "Test Description"
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(Report).where(Report.title == "New Test Report")
        test_report = session.exec(statement).first()
        if test_report:
            session.delete(test_report)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_delete_report():
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test report
    test_report = Report(
        title="Report to Delete",
        description="Test Description",
        duration=timedelta(hours=2),
        dead_time=timedelta(minutes=30),
        project_id=project_id,
        responsible_id=user_id
    )
    with Session(engine) as session:
        session.add(test_report)
        session.commit()
        session.refresh(test_report)
        report_id = test_report.id

    # Make the request to delete the report
    response = client.delete(f"/reports/{report_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Report deleted"

    # Verify the report was actually deleted
    with Session(engine) as session:
        statement = select(Report).where(Report.id == report_id)
        deleted_report = session.exec(statement).first()
        assert deleted_report is None

    # Clean up
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_update_report():
    """Test updating a report with valid data"""
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test report
    test_report = Report(
        title="Original Report",
        description="Original Description",
        duration=timedelta(hours=2),
        dead_time=timedelta(minutes=30),
        project_id=project_id,
        responsible_id=user_id
    )
    with Session(engine) as session:
        session.add(test_report)
        session.commit()
        session.refresh(test_report)
        report_id = test_report.id

    # Data for updating the report
    update_data = {
        "title": "Updated Report",
        "description": "Updated Description",
        "duration": "PT3H",  # 3 hours in ISO 8601 format
        "dead_time": "PT45M",  # 45 minutes in ISO 8601 format
        "dead_time_cause": "Technical issues",
        "project_id": project_id,
        "responsible_id": user_id
    }

    # Make the request to update the report
    response = client.put(f"/reports/{report_id}", json=update_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert data["title"] == "Updated Report"
    assert data["description"] == "Updated Description"
    assert data["duration"] == "PT3H"
    assert data["dead_time"] == "PT45M"
    assert data["dead_time_cause"] == "Technical issues"
    assert data["project_id"] == project_id
    assert data["responsible_id"] == user_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_report)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_update_report_not_found():
    """Test updating a non-existent report"""
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Data for updating the report
    update_data = {
        "title": "Updated Report",
        "description": "Updated Description",
        "duration": "PT3H",
        "dead_time": "PT45M",
        "project_id": project_id,
        "responsible_id": user_id
    }

    # Make the request to update a non-existent report
    response = client.put("/reports/999999", json=update_data)
    
    # Verify the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

    # Clean up
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_update_report_invalid_references():
    """Test updating a report with invalid foreign keys"""
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test report
    test_report = Report(
        title="Original Report",
        description="Original Description",
        duration=timedelta(hours=2),
        dead_time=timedelta(minutes=30),
        project_id=project_id,
        responsible_id=user_id
    )
    with Session(engine) as session:
        session.add(test_report)
        session.commit()
        session.refresh(test_report)
        report_id = test_report.id

    # Data for updating the report with invalid references
    update_data = {
        "title": "Updated Report",
        "description": "Updated Description",
        "duration": "PT3H",
        "dead_time": "PT45M",
        "project_id": 99999,      # Non-existent project
        "responsible_id": 99999   # Non-existent user
    }

    # Make the request to update the report
    response = client.put(f"/reports/{report_id}", json=update_data)
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower()

    # Clean up
    with Session(engine) as session:
        session.delete(test_report)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_update_report_partial():
    """Test updating a report with partial data"""
    # Create test dependencies
    user_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test report
    test_report = Report(
        title="Original Report",
        description="Original Description",
        duration=timedelta(hours=2),
        dead_time=timedelta(minutes=30),
        project_id=project_id,
        responsible_id=user_id
    )
    with Session(engine) as session:
        session.add(test_report)
        session.commit()
        session.refresh(test_report)
        report_id = test_report.id

    # Data for partial update
    update_data = {
        "title": "Updated Report",
        "dead_time_cause": "Technical issues"
    }

    # Make the request to update the report
    response = client.put(f"/reports/{report_id}", json=update_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert data["title"] == "Updated Report"
    assert data["description"] == "Original Description"  # Should remain unchanged
    assert data["dead_time_cause"] == "Technical issues"
    assert data["project_id"] == project_id
    assert data["responsible_id"] == user_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_report)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id, client_id)

def test_create_report_invalid_references():
    """Test creating a report with invalid foreign keys"""
    # Try to create a report with non-existent references
    new_report_data = {
        "title": "Invalid Report",
        "description": "Invalid Report Description",
        "duration": "02:00:00",
        "dead_time": "00:30:00",
        "project_id": 99999,      # Non-existent project
        "responsible_id": 99999   # Non-existent user
    }

    # Make the request to create a report
    response = client.post("/reports/", json=new_report_data)
    
    # Verify the response indicates an error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data  # Should contain error message 
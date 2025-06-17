from fastapi.testclient import TestClient
from app.main import app
from app.models import Photo, User, Report, Project, ProjectState, Client
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime, timedelta
import io
import os
from PIL import Image
from pathlib import Path

client = TestClient(app)

# Create a test image
def create_test_image(filename="test_image.jpg", size=(100, 100), color=(255, 0, 0)):
    """Create a simple test image and return its path"""
    img = Image.new('RGB', size, color=color)
    test_image_path = Path(filename)
    img.save(test_image_path)
    return test_image_path

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

def test_get_photos():
    """Test getting all photos"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test photo record (without actual file upload)
    test_photo = Photo(
        path="test/path/image.jpg",
        thumbnail="test/path/thumbnail.jpg",
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_photo)
        session.commit()
        session.refresh(test_photo)

    # Make the request to get all photos
    response = client.get("/photos/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Clean up
    with Session(engine) as session:
        session.delete(test_photo)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_get_single_photo():
    """Test getting a specific photo by ID"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test photo record
    test_photo = Photo(
        path="test/path/image.jpg",
        thumbnail="test/path/thumbnail.jpg",
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_photo)
        session.commit()
        session.refresh(test_photo)
        photo_id = test_photo.id

    # Make the request to get the specific photo
    response = client.get(f"/photos/{photo_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == photo_id
    assert data["path"] == "test/path/image.jpg"
    assert data["thumbnail"] == "test/path/thumbnail.jpg"
    assert data["report_id"] == report_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_photo)
        session.commit()
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_upload_photo():
    """Test uploading a new photo"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test image
    test_image_path = create_test_image()
    
    try:
        # Create the request with the test image
        with open(test_image_path, "rb") as img_file:
            response = client.post(
                "/photos/",
                files={"image": ("test_image.jpg", img_file, "image/jpeg")},
                data={"report_id": report_id}
            )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "path" in data
        assert "thumbnail" in data
        assert data["report_id"] == report_id
        
        # Verify the files were created
        assert os.path.exists(data["path"])
        assert os.path.exists(data["thumbnail"])
        
        # Clean up the uploaded files
        if os.path.exists(data["path"]):
            os.remove(data["path"])
        if os.path.exists(data["thumbnail"]):
            os.remove(data["thumbnail"])
        
        # Clean up the database record
        with Session(engine) as session:
            statement = select(Photo).where(Photo.id == data["id"])
            db_photo = session.exec(statement).first()
            if db_photo:
                session.delete(db_photo)
            session.commit()
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        # Clean up dependencies
        cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_upload_photo_invalid_report():
    """Test uploading a photo with invalid report ID"""
    # Create a test image
    test_image_path = create_test_image()
    
    try:
        # Create the request with the test image but invalid report ID
        with open(test_image_path, "rb") as img_file:
            response = client.post(
                "/photos/",
                files={"image": ("test_image.jpg", img_file, "image/jpeg")},
                data={"report_id": 99999} # Non-existent report ID
            )
        
        # Verify the response indicates an error
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_upload_photo_invalid_file():
    """Test uploading an invalid file type"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a text file instead of an image
    with open("test_file.txt", "w") as f:
        f.write("This is not an image")
    
    try:
        # Create the request with the test file
        with open("test_file.txt", "rb") as file:
            response = client.post(
                "/photos/",
                files={"image": ("test_file.txt", file, "text/plain")},
                data={"report_id": report_id}
            )
        
        # Verify the response indicates an error
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "must be an image" in data["detail"].lower()
    finally:
        # Clean up test file
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")
        
        # Clean up dependencies
        cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_delete_photo():
    """Test deleting a photo"""
    # Create test dependencies
    user_id, report_id, project_id, state_id, client_id = create_test_dependencies()
    
    # Create a test photo record
    test_photo = Photo(
        path="nonexistent/path/image.jpg",  # Using nonexistent path for testing deletion logic
        thumbnail="nonexistent/path/thumbnail.jpg",
        report_id=report_id
    )
    with Session(engine) as session:
        session.add(test_photo)
        session.commit()
        session.refresh(test_photo)
        photo_id = test_photo.id

    # Make the request to delete the photo
    response = client.delete(f"/photos/{photo_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Photo deleted"

    # Verify the photo was deleted from the database
    with Session(engine) as session:
        statement = select(Photo).where(Photo.id == photo_id)
        deleted_photo = session.exec(statement).first()
        assert deleted_photo is None

    # Clean up
    cleanup_test_dependencies(user_id, report_id, project_id, state_id, client_id)

def test_delete_nonexistent_photo():
    """Test deleting a photo that doesn't exist"""
    response = client.delete("/photos/99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower() 
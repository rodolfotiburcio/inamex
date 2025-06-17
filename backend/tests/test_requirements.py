from fastapi.testclient import TestClient
from app.main import app
from app.models import Requirement, RequirementState, Project, User, ProjectState, Article, ArticleState
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
        
        # Create test project state
        test_project_state = ProjectState(name="Test Project State")
        session.add(test_project_state)
        session.commit()
        session.refresh(test_project_state)
        
        # Create test project
        test_project = Project(
            number="TEST-001",
            name="Test Project",
            state_id=test_project_state.id
        )
        session.add(test_project)
        
        # Create test requirement state
        test_state = RequirementState(name="Test State")
        session.add(test_state)
        
        session.commit()
        session.refresh(test_user)
        session.refresh(test_project)
        session.refresh(test_state)
        
        return test_user.id, test_project.id, test_state.id

def cleanup_test_dependencies(user_id, project_id, state_id):
    """Helper function to clean up related entities"""
    with Session(engine) as session:
        # First delete all projects to avoid foreign key constraints
        projects = session.exec(select(Project)).all()
        for project in projects:
            session.delete(project)
        session.commit()
        
        # Then delete the rest of the entities
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            
        state = session.get(RequirementState, state_id)
        if state:
            session.delete(state)
            
        # Clean up project states
        project_states = session.exec(select(ProjectState)).all()
        for project_state in project_states:
            session.delete(project_state)
            
        session.commit()

def create_test_article_state():
    """Helper function to create a test article state"""
    with Session(engine) as session:
        test_article_state = ArticleState(
            name="Test Article State",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_article_state)
        session.commit()
        session.refresh(test_article_state)
        return test_article_state.id

def cleanup_test_article_state(article_state_id):
    """Helper function to clean up a test article state"""
    with Session(engine) as session:
        article_state = session.get(ArticleState, article_state_id)
        if article_state:
            session.delete(article_state)
            session.commit()

def test_get_requirements():
    # Create dependencies
    user_id, project_id, state_id = create_test_dependencies()
    
    # Create a test requirement
    test_requirement = Requirement(
        project_id=project_id,
        requested_by=user_id,
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_requirement)
        session.commit()
        session.refresh(test_requirement)

    # Make the request to get all requirements
    response = client.get("/requirements/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(req["project_id"] == project_id for req in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_requirement)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id)

def test_get_single_requirement():
    # Create dependencies
    user_id, project_id, state_id = create_test_dependencies()
    
    # Create a test requirement
    test_requirement = Requirement(
        project_id=project_id,
        requested_by=user_id,
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_requirement)
        session.commit()
        session.refresh(test_requirement)
        requirement_id = test_requirement.id

    # Make the request to get the specific requirement
    response = client.get(f"/requirements/{requirement_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert data["requested_by"] == user_id
    assert data["state_id"] == state_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_requirement)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id)

def test_create_requirement():
    """Test creating a requirement with valid data"""
    # Create test dependencies
    user_id, project_id, state_id = create_test_dependencies()
    
    # Data for creating a requirement
    requirement_data = {
        "project_id": project_id,
        "requested_by": user_id,
        "state_id": state_id
    }

    # Make the request to create a requirement
    response = client.post("/requirements/", json=requirement_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["project_id"] == project_id
    assert data["requested_by"] == user_id
    assert data["state_id"] == state_id

    # Clean up
    with Session(engine) as session:
        requirement = session.get(Requirement, data["id"])
        if requirement:
            session.delete(requirement)
            session.commit()
    cleanup_test_dependencies(user_id, project_id, state_id)

def test_create_requirement_with_articles():
    """Test creating a requirement with its articles"""
    # Create test dependencies
    user_id, project_id, state_id = create_test_dependencies()
    article_state_id = create_test_article_state()
    
    # Data for creating a requirement with articles
    requirement_data = {
        "requirement": {
            "project_id": project_id,
            "requested_by": user_id,
            "state_id": state_id
        },
        "articles": [
            {
                "quantity": "10.5",
                "unit": "pcs",
                "brand": "Test Brand 1",
                "model": "Test Model 1",
                "dimensions": "10x20x30",
                "state_id": article_state_id
            },
            {
                "quantity": "5.0",
                "unit": "kg",
                "brand": "Test Brand 2",
                "model": "Test Model 2",
                "dimensions": "15x25x35",
                "state_id": article_state_id
            }
        ]
    }

    # Make the request to create a requirement with articles
    response = client.post("/requirements/with-articles", json=requirement_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["project_id"] == project_id
    assert data["requested_by"] == user_id
    assert data["state_id"] == state_id

    # Verify that the articles were created and linked to the requirement
    with Session(engine) as session:
        requirement = session.get(Requirement, data["id"])
        assert requirement is not None
        
        statement = select(Article).where(Article.requirement_id == requirement.id)
        result = session.exec(statement)
        articles = result.all()
        assert len(articles) == 2
        
        # Verify that created_at and updated_at were set
        for article in articles:
            assert article.created_at is not None
            assert article.updated_at is not None
        
        # Clean up
        for article in articles:
            session.delete(article)
        session.delete(requirement)
        session.commit()
    
    cleanup_test_dependencies(user_id, project_id, state_id)
    cleanup_test_article_state(article_state_id)

def test_create_requirement_with_articles_invalid_references():
    """Test creating a requirement with articles using invalid references"""
    # Create test dependencies
    user_id, project_id, state_id = create_test_dependencies()
    article_state_id = create_test_article_state()
    
    # Data for creating a requirement with articles using invalid references
    requirement_data = {
        "requirement": {
            "project_id": 99999,  # Invalid project_id
            "requested_by": user_id,
            "state_id": state_id
        },
        "articles": [
            {
                "quantity": "10.5",
                "unit": "pcs",
                "brand": "Test Brand",
                "model": "Test Model",
                "dimensions": "10x20x30",
                "state_id": 99999  # Invalid article state_id
            }
        ]
    }

    # Make the request to create a requirement with articles
    response = client.post("/requirements/with-articles", json=requirement_data)
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower()

    # Clean up
    cleanup_test_dependencies(user_id, project_id, state_id)
    cleanup_test_article_state(article_state_id)

def test_delete_requirement():
    # Create dependencies
    user_id, project_id, state_id = create_test_dependencies()
    
    # Create a test requirement
    test_requirement = Requirement(
        project_id=project_id,
        requested_by=user_id,
        state_id=state_id
    )
    with Session(engine) as session:
        session.add(test_requirement)
        session.commit()
        session.refresh(test_requirement)
        requirement_id = test_requirement.id

    # Make the request to delete the requirement
    response = client.delete(f"/requirements/{requirement_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Requirement deleted"

    # Verify the requirement was actually deleted
    with Session(engine) as session:
        statement = select(Requirement).where(Requirement.id == requirement_id)
        deleted_requirement = session.exec(statement).first()
        assert deleted_requirement is None
    
    # Clean up dependencies
    cleanup_test_dependencies(user_id, project_id, state_id)

def test_create_requirement_invalid_references():
    """Test creating a requirement with invalid foreign keys"""
    # Try to create a requirement with non-existent references
    new_requirement_data = {
        "project_id": 99999,  # Non-existent project
        "requested_by": 99999,  # Non-existent user
        "state_id": 99999  # Non-existent state
    }

    # Make the request to create a requirement
    response = client.post("/requirements/", json=new_requirement_data)
    
    # Verify the response indicates an error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data  # Should contain error message 
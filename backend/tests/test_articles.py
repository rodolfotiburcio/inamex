from fastapi.testclient import TestClient
from app.main import app
from app.models import Article, ArticleState, Requirement, RequirementState, Project, ProjectState, User
from app.core.database import engine, get_session
from sqlmodel import Session, select
from decimal import Decimal
import pytest

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
        session.commit()
        session.refresh(test_user)
        
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
        session.commit()
        session.refresh(test_project)
        
        # Create test requirement state
        test_requirement_state = RequirementState(name="Test Requirement State")
        session.add(test_requirement_state)
        session.commit()
        session.refresh(test_requirement_state)
        
        # Create test article state
        test_article_state = ArticleState(name="Test Article State")
        session.add(test_article_state)
        session.commit()
        session.refresh(test_article_state)
        
        # Create test requirement
        test_requirement = Requirement(
            project_id=test_project.id,
            requested_by=test_user.id,
            state_id=test_requirement_state.id
        )
        session.add(test_requirement)
        session.commit()
        session.refresh(test_requirement)
        
        return (
            test_user.id,
            test_project.id,
            test_requirement_state.id,
            test_article_state.id,
            test_requirement.id
        )

def cleanup_test_dependencies(user_id, project_id, requirement_state_id, article_state_id, requirement_id):
    """Helper function to clean up related entities"""
    with Session(engine) as session:
        # Delete requirement
        requirement = session.get(Requirement, requirement_id)
        if requirement:
            session.delete(requirement)
            
        # Delete user
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            
        # Delete project
        project = session.get(Project, project_id)
        if project:
            session.delete(project)
            
        # Delete requirement state
        requirement_state = session.get(RequirementState, requirement_state_id)
        if requirement_state:
            session.delete(requirement_state)
            
        # Delete article state
        article_state = session.get(ArticleState, article_state_id)
        if article_state:
            session.delete(article_state)
            
        session.commit()

def test_get_articles():
    # Create dependencies
    user_id, project_id, requirement_state_id, article_state_id, requirement_id = create_test_dependencies()
    
    # Create a test article
    test_article = Article(
        requirement_id=requirement_id,
        requirement_consecutive=1,
        quantity=Decimal("10.5"),
        unit="pcs",
        brand="Test Brand",
        model="Test Model",
        dimensions="10x20x30",
        state_id=article_state_id,
        notes="Test notes"
    )
    with Session(engine) as session:
        session.add(test_article)
        session.commit()
        session.refresh(test_article)

    # Make the request to get all articles
    response = client.get("/articles/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(article["requirement_id"] == requirement_id for article in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_article)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, requirement_state_id, article_state_id, requirement_id)

def test_get_single_article():
    # Create dependencies
    user_id, project_id, requirement_state_id, article_state_id, requirement_id = create_test_dependencies()
    
    # Create a test article
    test_article = Article(
        requirement_id=requirement_id,
        requirement_consecutive=1,
        quantity=Decimal("10.5"),
        unit="pcs",
        brand="Test Brand",
        model="Test Model",
        dimensions="10x20x30",
        state_id=article_state_id,
        notes="Test notes"
    )
    with Session(engine) as session:
        session.add(test_article)
        session.commit()
        session.refresh(test_article)
    article_id = test_article.id

    # Make the request to get the specific article
    response = client.get(f"/articles/{article_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["requirement_id"] == requirement_id
    assert data["requirement_consecutive"] == 1
    assert data["quantity"] == "10.5"
    assert data["unit"] == "pcs"
    assert data["brand"] == "Test Brand"
    assert data["model"] == "Test Model"
    assert data["dimensions"] == "10x20x30"
    assert data["state_id"] == article_state_id
    assert data["notes"] == "Test notes"

    # Clean up
    with Session(engine) as session:
        session.delete(test_article)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, requirement_state_id, article_state_id, requirement_id)

def test_create_article():
    # Create dependencies
    user_id, project_id, requirement_state_id, article_state_id, requirement_id = create_test_dependencies()
    
    # Data for the new article
    new_article_data = {
        "requirement_id": requirement_id,
        "requirement_consecutive": 1,
        "quantity": "10.5",
        "unit": "pcs",
        "brand": "Test Brand",
        "model": "Test Model",
        "dimensions": "10x20x30",
        "state_id": article_state_id,
        "notes": "Test notes"
    }

    # Make the request to create an article
    response = client.post("/articles/", json=new_article_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["requirement_id"] == requirement_id
    assert data["requirement_consecutive"] == 1
    assert data["quantity"] == "10.5"
    assert data["unit"] == "pcs"
    assert data["brand"] == "Test Brand"
    assert data["model"] == "Test Model"
    assert data["dimensions"] == "10x20x30"
    assert data["state_id"] == article_state_id
    assert data["notes"] == "Test notes"

    # Verify the database state
    with Session(engine) as session:
        db_article = session.get(Article, data["id"])
        assert db_article.requirement_id == requirement_id
        assert db_article.requirement_consecutive == 1
        assert db_article.quantity == Decimal("10.5")
        assert db_article.unit == "pcs"
        assert db_article.brand == "Test Brand"
        assert db_article.model == "Test Model"
        assert db_article.dimensions == "10x20x30"
        assert db_article.state_id == article_state_id
        assert db_article.notes == "Test notes"
        
        # Clean up
        session.delete(db_article)
        session.commit()
    cleanup_test_dependencies(user_id, project_id, requirement_state_id, article_state_id, requirement_id)

def test_delete_article():
    # Create dependencies
    user_id, project_id, requirement_state_id, article_state_id, requirement_id = create_test_dependencies()
    
    # Create a test article
    test_article = Article(
        requirement_id=requirement_id,
        requirement_consecutive=1,
        quantity=Decimal("10.5"),
        unit="pcs",
        brand="Brand to Delete",
        model="Model to Delete",
        dimensions="10x20x30",
        state_id=article_state_id
    )
    with Session(engine) as session:
        session.add(test_article)
        session.commit()
        session.refresh(test_article)
    article_id = test_article.id

    # Make the request to delete the article
    response = client.delete(f"/articles/{article_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Article deleted"

    # Verify the article was actually deleted
    with Session(engine) as session:
        db_article = session.get(Article, article_id)
        assert db_article is None
    
    # Clean up dependencies
    cleanup_test_dependencies(user_id, project_id, requirement_state_id, article_state_id, requirement_id)

def test_create_article_invalid_references():
    """Test creating an article with invalid foreign keys"""
    # Try to create an article with non-existent references
    new_article_data = {
        "requirement_id": 99999,  # Non-existent requirement
        "requirement_consecutive": 1,
        "quantity": "10.5",
        "unit": "pcs",
        "brand": "Test Brand",
        "model": "Test Model",
        "dimensions": "10x20x30",
        "state_id": 99999  # Non-existent state
    }

    # Make the request to create an article
    response = client.post("/articles/", json=new_article_data)
    
    # Verify the response indicates an error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data  # Should contain error message

def test_update_article():
    article_id = None
    project_id = None
    requirement_id = None
    state_id = None
    requirement_state_id = None
    project_state_id = None
    
    # Create a requirement state first
    with Session(engine) as session:
        # Create a project state first
        project_state = ProjectState(
            name="Test Project State",
            description="Test Description",
            order=1
        )
        session.add(project_state)
        session.commit()
        session.refresh(project_state)
        project_state_id = project_state.id
        
        # Create a project
        project = Project(
            number="TEST-001",
            name="Test Project",
            state_id=project_state.id
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        project_id = project.id
        
        requirement_state = RequirementState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(requirement_state)
        session.commit()
        session.refresh(requirement_state)
        requirement_state_id = requirement_state.id
        
        # Create a requirement
        requirement = Requirement(
            project_id=project.id,
            consecutive=1,
            name="Test Requirement",
            description="Test Description",
            state_id=requirement_state.id
        )
        session.add(requirement)
        session.commit()
        session.refresh(requirement)
        requirement_id = requirement.id
        
        # Create an article state
        state = ArticleState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(state)
        session.commit()
        session.refresh(state)
        state_id = state.id
        
        # Create an article
        article = Article(
            requirement_id=requirement.id,
            requirement_consecutive=1,
            quantity=Decimal("10.5"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x10x10",
            state_id=state.id,
            notes="Test Notes"
        )
        session.add(article)
        session.commit()
        session.refresh(article)
        article_id = article.id
        
        # Update the article
        update_data = {
            "quantity": "15.5",
            "unit": "kg",
            "brand": "Updated Brand",
            "model": "Updated Model",
            "dimensions": "20x20x20",
            "notes": "Updated Notes"
        }
        
        response = client.put(f"/articles/{article.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article.id
        assert data["quantity"] == "15.5"
        assert data["unit"] == "kg"
        assert data["brand"] == "Updated Brand"
        assert data["model"] == "Updated Model"
        assert data["dimensions"] == "20x20x20"
        assert data["notes"] == "Updated Notes"
    
    # Verify the database state with a new session
    with Session(engine) as session:
        db_article = session.get(Article, article_id)
        assert db_article is not None
        assert db_article.quantity == Decimal("15.5")
        assert db_article.unit == "kg"
        assert db_article.brand == "Updated Brand"
        assert db_article.model == "Updated Model"
        assert db_article.dimensions == "20x20x20"
        assert db_article.notes == "Updated Notes"
    
    # Clean up in the correct order
    with Session(engine) as session:
        # First delete the article
        article = session.get(Article, article_id)
        if article:
            session.delete(article)
        
        # Then delete the article state
        state = session.get(ArticleState, state_id)
        if state:
            session.delete(state)
        
        # Then delete the requirement
        requirement = session.get(Requirement, requirement_id)
        if requirement:
            session.delete(requirement)
        
        # Then delete the requirement state
        requirement_state = session.get(RequirementState, requirement_state_id)
        if requirement_state:
            session.delete(requirement_state)
        
        # Then delete the project
        project = session.get(Project, project_id)
        if project:
            session.delete(project)
        
        # Finally delete the project state
        project_state = session.get(ProjectState, project_state_id)
        if project_state:
            session.delete(project_state)
        
        session.commit()

def test_update_article_partial():
    article_id = None
    state_id = None
    requirement_id = None
    requirement_state_id = None
    project_id = None
    project_state_id = None
    
    # Create a requirement state first
    with Session(engine) as session:
        # Create a project state first
        project_state = ProjectState(
            name="Test Project State",
            description="Test Description",
            order=1
        )
        session.add(project_state)
        session.commit()
        session.refresh(project_state)
        project_state_id = project_state.id
        
        # Create a project
        project = Project(
            number="TEST-001",
            name="Test Project",
            state_id=project_state.id
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        project_id = project.id
        
        requirement_state = RequirementState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(requirement_state)
        session.commit()
        session.refresh(requirement_state)
        requirement_state_id = requirement_state.id
        
        # Create a requirement
        requirement = Requirement(
            project_id=project.id,
            consecutive=1,
            name="Test Requirement",
            description="Test Description",
            state_id=requirement_state.id
        )
        session.add(requirement)
        session.commit()
        session.refresh(requirement)
        requirement_id = requirement.id
        
        # Create an article state
        state = ArticleState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(state)
        session.commit()
        session.refresh(state)
        state_id = state.id
        
        # Create an article
        article = Article(
            requirement_id=requirement.id,
            requirement_consecutive=1,
            quantity=Decimal("10.5"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x10x10",
            state_id=state.id,
            notes="Test Notes"
        )
        session.add(article)
        session.commit()
        session.refresh(article)
        article_id = article.id
        
        # Update only some fields
        update_data = {
            "brand": "Updated Brand",
            "notes": "Updated Notes"
        }
        
        response = client.put(f"/articles/{article.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article.id
        assert data["brand"] == "Updated Brand"
        assert data["notes"] == "Updated Notes"
        # Verify other fields remain unchanged
        assert data["quantity"] == "10.5"
        assert data["unit"] == "pcs"
        assert data["model"] == "Test Model"
        assert data["dimensions"] == "10x10x10"
    
    # Verify the database state with a new session
    with Session(engine) as session:
        db_article = session.get(Article, article_id)
        assert db_article is not None
        assert db_article.brand == "Updated Brand"
        assert db_article.notes == "Updated Notes"
        assert db_article.quantity == Decimal("10.5")
        assert db_article.unit == "pcs"
        assert db_article.model == "Test Model"
        assert db_article.dimensions == "10x10x10"
    
    # Clean up in the correct order
    with Session(engine) as session:
        # First delete the article
        article = session.get(Article, article_id)
        if article:
            session.delete(article)
        
        # Then delete the article state
        state = session.get(ArticleState, state_id)
        if state:
            session.delete(state)
        
        # Then delete the requirement
        requirement = session.get(Requirement, requirement_id)
        if requirement:
            session.delete(requirement)
        
        # Then delete the requirement state
        requirement_state = session.get(RequirementState, requirement_state_id)
        if requirement_state:
            session.delete(requirement_state)
        
        # Then delete the project
        project = session.get(Project, project_id)
        if project:
            session.delete(project)
        
        # Finally delete the project state
        project_state = session.get(ProjectState, project_state_id)
        if project_state:
            session.delete(project_state)
        
        session.commit()

def test_update_article_not_found():
    update_data = {
        "brand": "Updated Brand"
    }
    response = client.put("/articles/999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"

def test_update_article_invalid_requirement():
    # Create a requirement state first
    with Session(engine) as session:
        requirement_state = RequirementState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(requirement_state)
        session.commit()
        session.refresh(requirement_state)
        
        # Create an article state
        state = ArticleState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(state)
        session.commit()
        session.refresh(state)
        
        # Create an article
        article = Article(
            requirement_id=None,
            requirement_consecutive=1,
            quantity=Decimal("10.5"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x10x10",
            state_id=state.id,
            notes="Test Notes"
        )
        session.add(article)
        session.commit()
        session.refresh(article)
        
        # Try to update with invalid requirement_id
        update_data = {
            "requirement_id": 999
        }
        response = client.put(f"/articles/{article.id}", json=update_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid requirement_id"
        
        # Clean up
        session.delete(article)
        session.delete(state)
        session.delete(requirement_state)
        session.commit()

def test_update_article_invalid_state():
    # Create a requirement state first
    with Session(engine) as session:
        # Create a project state first
        project_state = ProjectState(
            name="Test Project State",
            description="Test Description",
            order=1
        )
        session.add(project_state)
        session.commit()
        session.refresh(project_state)
        
        # Create a project
        project = Project(
            number="TEST-001",
            name="Test Project",
            state_id=project_state.id
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        
        requirement_state = RequirementState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(requirement_state)
        session.commit()
        session.refresh(requirement_state)
        
        # Create a requirement
        requirement = Requirement(
            project_id=project.id,
            consecutive=1,
            name="Test Requirement",
            description="Test Description",
            state_id=requirement_state.id
        )
        session.add(requirement)
        session.commit()
        session.refresh(requirement)
        
        # Create an article state
        state = ArticleState(
            name="Test State",
            description="Test Description",
            order=1
        )
        session.add(state)
        session.commit()
        session.refresh(state)
        
        # Create an article
        article = Article(
            requirement_id=requirement.id,
            requirement_consecutive=1,
            quantity=Decimal("10.5"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x10x10",
            state_id=state.id,
            notes="Test Notes"
        )
        session.add(article)
        session.commit()
        session.refresh(article)
        
        # Try to update with invalid state_id
        update_data = {
            "state_id": 999
        }
        response = client.put(f"/articles/{article.id}", json=update_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid state_id"
        
        # Clean up
        session.delete(article)
        session.delete(state)
        session.delete(requirement)
        session.delete(requirement_state)
        session.delete(project)
        session.delete(project_state)
        session.commit() 
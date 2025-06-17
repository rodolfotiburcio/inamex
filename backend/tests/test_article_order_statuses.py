from fastapi.testclient import TestClient
from app.main import app
from app.models import ArticleOrderStatus
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime

client = TestClient(app)

def test_get_article_order_statuses():
    # Create a test article order status
    test_status = ArticleOrderStatus(name="Test Status")
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)

    # Make the request to get all statuses
    response = client.get("/article-order-statuses/")
    
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

def test_get_single_article_order_status():
    # Create a test article order status
    test_status = ArticleOrderStatus(name="Single Test Status")
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)
        status_id = test_status.id

    # Make the request to get the specific status
    response = client.get(f"/article-order-statuses/{status_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test Status"
    assert data["id"] == status_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_status)
        session.commit()

def test_get_nonexistent_article_order_status():
    response = client.get("/article-order-statuses/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article order status not found"

def test_create_article_order_status():
    # Data for the new status
    new_status_data = {
        "name": "New Test Status",
        "description": "Test Description",
        "order": 1,
        "active": True
    }

    # Make the request to create a status
    response = client.post("/article-order-statuses/", json=new_status_data)
    
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
        statement = select(ArticleOrderStatus).where(ArticleOrderStatus.name == "New Test Status")
        test_status = session.exec(statement).first()
        if test_status:
            session.delete(test_status)
            session.commit()

def test_create_duplicate_article_order_status():
    # Create initial status
    test_status = ArticleOrderStatus(
        name="Duplicate Status",
        description="Test Description",
        order=1,
        active=True
    )
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)

    # Try to create duplicate
    response = client.post(
        "/article-order-statuses/",
        json={
            "name": "Duplicate Status",
            "description": "Another Description",
            "order": 2,
            "active": True
        }
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

    # Clean up
    with Session(engine) as session:
        session.delete(test_status)
        session.commit()

def test_delete_article_order_status():
    # Create a test article order status
    test_status = ArticleOrderStatus(name="Condition To Delete")
    with Session(engine) as session:
        session.add(test_status)
        session.commit()
        session.refresh(test_status)
        status_id = test_status.id

    # Make the request to delete the status
    response = client.delete(f"/article-order-statuses/{status_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Article order status deleted"

    # Verify the status was actually deleted
    with Session(engine) as session:
        statement = select(ArticleOrderStatus).where(ArticleOrderStatus.id == status_id)
        deleted_status = session.exec(statement).first()
        assert deleted_status is None

def test_delete_nonexistent_article_order_status():
    response = client.delete("/article-order-statuses/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article order status not found"

def test_update_article_order_status():
    """Test updating an article order status"""
    # Create a test status
    test_status = ArticleOrderStatus(
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
        f"/article-order-statuses/{status_id}",
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
        updated_status = session.get(ArticleOrderStatus, status_id)
        assert updated_status.name == "Updated Status"
        assert updated_status.description == "Updated Description"
        assert updated_status.order == 2
        assert updated_status.active == False
        assert updated_status.created_at == original_created_at
        assert updated_status.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_status)
        session.commit()

def test_update_article_order_status_partial():
    """Test updating only some fields of an article order status"""
    # Create a test status
    test_status = ArticleOrderStatus(
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
        f"/article-order-statuses/{status_id}",
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
        updated_status = session.get(ArticleOrderStatus, status_id)
        assert updated_status.name == "Partially Updated Status"
        assert updated_status.description == "Original Description"
        assert updated_status.order == 1
        assert updated_status.active == True
        assert updated_status.created_at == original_created_at
        assert updated_status.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_status)
        session.commit()

def test_update_article_order_status_not_found():
    """Test updating a non-existent article order status"""
    response = client.put(
        "/article-order-statuses/999999",  # ID that surely doesn't exist
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Article order status not found" in response.json()["detail"]

def test_update_article_order_status_name_conflict():
    """Test updating an article order status with a name that already exists"""
    # Create two test statuses
    test_status1 = ArticleOrderStatus(name="Status One")
    test_status2 = ArticleOrderStatus(name="Status Two")
    with Session(engine) as session:
        session.add(test_status1)
        session.add(test_status2)
        session.commit()
        session.refresh(test_status1)
        session.refresh(test_status2)
        status1_id = test_status1.id
        status2_id = test_status2.id
    
    # Try to update status1 with status2's name
    response = client.put(
        f"/article-order-statuses/{status1_id}",
        json={
            "name": "Status Two"
        }
    )
    
    assert response.status_code == 409
    assert "Article order status with name 'Status Two' already exists" in response.json()["detail"]
    
    # Cleanup
    with Session(engine) as session:
        session.delete(test_status1)
        session.delete(test_status2)
        session.commit() 
from fastapi.testclient import TestClient
from app.main import app
from app.models.budget import Budget
from app.models.client import Client
from app.models.contact import Contact
from app.models.project import Project
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.project_state import ProjectState

# Create test client
test_client = TestClient(app)

def test_create_budget():
    # Create a test client and contact
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

        test_contact = Contact(name="Test Contact", client_id=client_id)
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

    budget_data = {
        "number": 1,
        "name": "Test Budget",
        "client_id": client_id,
        "contact_id": contact_id,
        "delivery_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    response = test_client.post("/budgets/", json=budget_data)
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == budget_data["number"]
    assert data["name"] == budget_data["name"]
    assert data["client_id"] == budget_data["client_id"]
    assert data["contact_id"] == budget_data["contact_id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up
    with Session(engine) as session:
        # First delete the budget
        statement = select(Budget).where(Budget.client_id == client_id)
        budgets = session.exec(statement).all()
        for budget in budgets:
            session.delete(budget)
        session.commit()

        # Then delete the contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Finally delete the client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_create_budget_invalid_client():
    """Test creating a budget with non-existent client"""
    budget_data = {
        "number": 1,
        "name": "Test Budget",
        "client_id": 999999,  # Non-existent client ID
        "contact_id": 1,
        "delivery_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    response = test_client.post("/budgets/", json=budget_data)
    assert response.status_code == 404
    assert "Client not found" in response.json()["detail"]

def test_create_budget_invalid_contact():
    """Test creating a budget with non-existent contact"""
    # Create a test client
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

    budget_data = {
        "number": 1,
        "name": "Test Budget",
        "client_id": client_id,
        "contact_id": 999999,  # Non-existent contact ID
        "delivery_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    response = test_client.post("/budgets/", json=budget_data)
    assert response.status_code == 404
    assert "Contact not found" in response.json()["detail"]

    # Clean up
    with Session(engine) as session:
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_create_budget_contact_wrong_client():
    """Test creating a budget with contact from different client"""
    # Create two test clients
    with Session(engine) as session:
        client1 = Client(name="Test Client 1")
        client2 = Client(name="Test Client 2")
        session.add(client1)
        session.add(client2)
        session.commit()
        session.refresh(client1)
        session.refresh(client2)
        client1_id = client1.id
        client2_id = client2.id

        # Create a contact for client2
        contact = Contact(name="Test Contact", client_id=client2_id)
        session.add(contact)
        session.commit()
        session.refresh(contact)
        contact_id = contact.id

    budget_data = {
        "number": 1,
        "name": "Test Budget",
        "client_id": client1_id,  # Using client1
        "contact_id": contact_id,  # But contact belongs to client2
        "delivery_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    response = test_client.post("/budgets/", json=budget_data)
    assert response.status_code == 400
    assert "Contact does not belong to the specified client" in response.json()["detail"]

    # Clean up
    with Session(engine) as session:
        # Delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Delete clients
        client1 = session.get(Client, client1_id)
        client2 = session.get(Client, client2_id)
        if client1:
            session.delete(client1)
        if client2:
            session.delete(client2)
        session.commit()

def test_read_budgets():
    # Create test data
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

        test_contact = Contact(name="Test Contact", client_id=client_id)
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

        budget1 = Budget(
            number=1,
            name="Budget 1",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=30)
        )
        budget2 = Budget(
            number=2,
            name="Budget 2",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=60)
        )
        session.add(budget1)
        session.add(budget2)
        session.commit()

    response = test_client.get("/budgets/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(b["name"] == "Budget 1" and b["number"] == 1 for b in data)
    assert any(b["name"] == "Budget 2" and b["number"] == 2 for b in data)

    # Clean up
    with Session(engine) as session:
        # Delete budgets
        statement = select(Budget).where(Budget.client_id == client_id)
        budgets = session.exec(statement).all()
        for budget in budgets:
            session.delete(budget)
        session.commit()

        # Delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_read_budget():
    # Create test data
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

        test_contact = Contact(name="Test Contact", client_id=client_id)
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

        budget = Budget(
            number=1,
            name="Test Budget",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=30)
        )
        session.add(budget)
        session.commit()
        session.refresh(budget)
        budget_id = budget.id

    response = test_client.get(f"/budgets/{budget_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 1
    assert data["name"] == "Test Budget"
    assert data["client_id"] == client_id
    assert data["contact_id"] == contact_id
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up
    with Session(engine) as session:
        # Delete budget
        budget = session.get(Budget, budget_id)
        if budget:
            session.delete(budget)
            session.commit()

        # Delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_read_budget_not_found():
    """Test reading a non-existent budget"""
    response = test_client.get("/budgets/999999")
    assert response.status_code == 404
    assert "Budget not found" in response.json()["detail"]

def test_update_budget():
    # Create test data
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

        test_contact = Contact(name="Test Contact", client_id=client_id)
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

        budget = Budget(
            number=1,
            name="Test Budget",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=30)
        )
        session.add(budget)
        session.commit()
        session.refresh(budget)
        budget_id = budget.id
        original_created_at = budget.created_at

    update_data = {
        "number": 2,
        "name": "Updated Budget",
        "delivery_date": (datetime.utcnow() + timedelta(days=60)).isoformat()
    }

    response = test_client.put(f"/budgets/{budget_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == update_data["number"]
    assert data["name"] == update_data["name"]
    assert "created_at" in data
    assert "updated_at" in data
    # Verify created_at didn't change
    assert data["created_at"] == original_created_at.isoformat()
    # Verify updated_at did change
    assert data["updated_at"] > original_created_at.isoformat()

    # Clean up
    with Session(engine) as session:
        # Delete budget
        budget = session.get(Budget, budget_id)
        if budget:
            session.delete(budget)
            session.commit()

        # Delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_update_budget_not_found():
    """Test updating a non-existent budget"""
    update_data = {
        "number": 2,
        "name": "Updated Budget",
        "delivery_date": (datetime.utcnow() + timedelta(days=60)).isoformat()
    }
    response = test_client.put("/budgets/999999", json=update_data)
    assert response.status_code == 404
    assert "Budget not found" in response.json()["detail"]

def test_delete_budget():
    # Create test data
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

        test_contact = Contact(name="Test Contact", client_id=client_id)
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

        budget = Budget(
            number=1,
            name="Test Budget",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=30)
        )
        session.add(budget)
        session.commit()
        session.refresh(budget)
        budget_id = budget.id

    response = test_client.delete(f"/budgets/{budget_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Budget deleted"}

    # Verify budget is deleted
    with Session(engine) as session:
        deleted_budget = session.get(Budget, budget_id)
        assert deleted_budget is None

    # Clean up
    with Session(engine) as session:
        # Delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_delete_budget_not_found():
    """Test deleting a non-existent budget"""
    response = test_client.delete("/budgets/999999")
    assert response.status_code == 404
    assert "Budget not found" in response.json()["detail"]

def test_delete_budget_with_project():
    """Test deleting a budget that is associated with a project"""
    # Create test data
    with Session(engine) as session:
        # Create test client
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id

        # Create test contact
        test_contact = Contact(name="Test Contact", client_id=client_id)
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

        # Create test budget
        budget = Budget(
            number=1,
            name="Test Budget",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=30)
        )
        session.add(budget)
        session.commit()
        session.refresh(budget)
        budget_id = budget.id

        # Create test project state
        test_state = ProjectState(
            name="Test State",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_state)
        session.commit()
        session.refresh(test_state)

        # Create test project
        project = Project(
            number="TEST-001",
            name="Test Project",
            client_id=client_id,
            budget_id=budget_id,
            state_id=test_state.id
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        # Try to delete the budget
        response = test_client.delete(f"/budgets/{budget_id}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot delete budget that is associated with a project"

        # Clean up
        session.delete(project)
        session.delete(budget)
        session.delete(test_contact)
        session.delete(test_client_db)
        session.delete(test_state)
        session.commit() 
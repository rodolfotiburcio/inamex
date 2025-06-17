from fastapi.testclient import TestClient
from app.main import app
from app.models import Client, Project, Contact, Budget, ProjectState
from app.core.database import engine
from sqlmodel import Session, select
from datetime import datetime, timedelta

client = TestClient(app)

def test_get_clients():
    # Create a test client in the database
    test_client = Client(name="Test Client")
    with Session(engine) as session:
        session.add(test_client)
        session.commit()
        session.refresh(test_client)

    # Make the request to get all clients
    response = client.get("/clients/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    found_client = next((c for c in data if c["name"] == "Test Client"), None)
    assert found_client is not None
    assert "created_at" in found_client
    assert "updated_at" in found_client

    # Clean up
    with Session(engine) as session:
        statement = select(Client).where(Client.name == "Test Client")
        test_client = session.exec(statement).first()
        if test_client:
            session.delete(test_client)
            session.commit()

def test_get_single_client():
    # Create a test client in the database
    test_client = Client(name="Test Single Client")
    with Session(engine) as session:
        session.add(test_client)
        session.commit()
        session.refresh(test_client)
        client_id = test_client.id

    # Make the request to get the specific client
    response = client.get(f"/clients/{client_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Single Client"
    assert data["id"] == client_id
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up
    with Session(engine) as session:
        session.delete(test_client)
        session.commit()

def test_get_full_client():
    # Create test data
    with Session(engine) as session:
        # Create test client
        test_client = Client(name="Test Full Client")
        session.add(test_client)
        session.commit()
        session.refresh(test_client)
        client_id = test_client.id

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

        # Create test contact
        test_contact = Contact(
            name="Test Contact",
            email="test@example.com",
            phone="1234567890",
            position="Manager",
            client_id=client_id
        )
        session.add(test_contact)
        session.commit()
        session.refresh(test_contact)
        contact_id = test_contact.id

        # Create test budget
        test_budget = Budget(
            number=1,
            name="Test Budget",
            client_id=client_id,
            contact_id=contact_id,
            delivery_date=datetime.utcnow() + timedelta(days=30)
        )
        session.add(test_budget)
        session.commit()
        session.refresh(test_budget)

        # Create test projects
        for i in range(6):  # Create 6 projects to test limit of 5
            project = Project(
                number=f"TEST-{i:03d}",
                name=f"Test Project {i}",
                client_id=client_id,
                state_id=test_state.id,
                date=datetime.utcnow() - timedelta(days=i)
            )
            session.add(project)
        session.commit()

    # Make the request to get the full client
    response = client.get(f"/clients/fullclient/{client_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Full Client"
    assert data["id"] == client_id
    assert "created_at" in data
    assert "updated_at" in data
    
    # Verify latest projects (should be 5 most recent)
    assert len(data["latest_projects"]) == 5
    project_dates = [datetime.fromisoformat(p["date"]) for p in data["latest_projects"]]
    assert all(project_dates[i] >= project_dates[i+1] for i in range(len(project_dates)-1))
    
    # Verify latest contacts
    assert len(data["latest_contacts"]) == 1
    assert data["latest_contacts"][0]["name"] == "Test Contact"
    assert data["latest_contacts"][0]["email"] == "test@example.com"
    assert data["latest_contacts"][0]["phone"] == "1234567890"
    assert data["latest_contacts"][0]["position"] == "Manager"
    
    # Verify latest budgets
    assert len(data["latest_budgets"]) == 1
    assert data["latest_budgets"][0]["name"] == "Test Budget"
    assert data["latest_budgets"][0]["contact_id"] == contact_id

    # Clean up
    with Session(engine) as session:
        # Delete projects
        statement = select(Project).where(Project.client_id == client_id)
        projects = session.exec(statement).all()
        for project in projects:
            session.delete(project)
        
        # Delete budget
        statement = select(Budget).where(Budget.client_id == client_id)
        budgets = session.exec(statement).all()
        for budget in budgets:
            session.delete(budget)
        
        # Delete contact
        statement = select(Contact).where(Contact.client_id == client_id)
        contacts = session.exec(statement).all()
        for contact in contacts:
            session.delete(contact)
        
        # Delete project state
        session.delete(test_state)
        
        # Delete client
        session.delete(test_client)
        session.commit()

def test_create_client():
    response = client.post(
        "/clients",
        json={"name": "Test Client"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Client"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up
    with Session(engine) as session:
        statement = select(Client).where(Client.name == "Test Client")
        test_client = session.exec(statement).first()
        if test_client:
            session.delete(test_client)
            session.commit()

def test_delete_client():
    # First create a client to delete
    create_response = client.post(
        "/clients",
        json={"name": "Client to Delete"}
    )
    assert create_response.status_code == 200
    client_id = create_response.json()["id"]

    # Now delete it
    delete_response = client.delete(f"/clients/{client_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Client deleted"}

    # Verify it's deleted
    get_response = client.get(f"/clients/{client_id}")
    assert get_response.status_code == 404 

def test_update_client():
    """Test updating a client"""
    # Create a test client
    test_client = Client(name="Original Client Name")
    with Session(engine) as session:
        session.add(test_client)
        session.commit()
        session.refresh(test_client)
        client_id = test_client.id
        original_created_at = test_client.created_at
    
    # Update the client name
    response = client.put(
        f"/clients/{client_id}",
        json={
            "name": "Updated Client Name"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    assert data["name"] == "Updated Client Name"
    assert "created_at" in data
    assert "updated_at" in data
    # Verificar que el created_at no cambia
    assert data["created_at"] == original_created_at.isoformat()
    # Verificar que el updated_at sí cambia
    assert datetime.fromisoformat(data["updated_at"]) > original_created_at
    
    # Verify that it was updated in the database
    with Session(engine) as session:
        updated_client = session.get(Client, client_id)
        assert updated_client.name == "Updated Client Name"
        assert updated_client.created_at == original_created_at
        assert updated_client.updated_at > original_created_at
        
        # Cleanup
        session.delete(updated_client)
        session.commit()

def test_update_client_duplicate_name():
    """Test that updating a client with an existing name fails"""
    # Create two clients
    client1 = Client(name="Client One")
    client2 = Client(name="Client Two")
    with Session(engine) as session:
        session.add(client1)
        session.add(client2)
        session.commit()
        session.refresh(client1)
        session.refresh(client2)
        client1_id = client1.id
        client2_id = client2.id
    
    # Try to update client2 with the name of client1
    response = client.put(
        f"/clients/{client2_id}",
        json={
            "name": "Client One"
        }
    )
    
    assert response.status_code == 400
    assert "Client name already exists" in response.json()["detail"]
    
    # Verify it didn't change
    with Session(engine) as session:
        unchanged_client = session.get(Client, client2_id)
        assert unchanged_client.name == "Client Two"
        
        # Cleanup
        session.delete(session.get(Client, client1_id))
        session.delete(unchanged_client)
        session.commit()

def test_update_client_not_found():
    """Test updating a non-existent client"""
    response = client.put(
        "/clients/999999",  # ID that probably doesn't exist
        json={
            "name": "This Won't Update"
        }
    )
    assert response.status_code == 404
    assert "Client not found" in response.json()["detail"] 
from fastapi.testclient import TestClient
from app.main import app
from app.models.contact import Contact
from app.models.client import Client
from app.core.database import engine
from sqlmodel import Session, select

# Create test client
test_client = TestClient(app)

def test_create_contact():
    # Create a test client first
    test_client_db = Client(name="Test Client")
    with Session(engine) as session:
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)

    contact_data = {
        "name": "Test Contact",
        "client_id": test_client_db.id
    }

    response = test_client.post("/contacts/", json=contact_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert data["client_id"] == test_client_db.id
    assert data["email"] is None
    assert data["phone"] is None
    assert data["position"] is None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up - first delete the contact, then the client
    with Session(engine) as session:
        # First delete all contacts associated with the client
        statement = select(Contact).where(Contact.client_id == test_client_db.id)
        contacts = session.exec(statement).all()
        for contact in contacts:
            session.delete(contact)
        session.commit()

        # Then delete the client
        client = session.get(Client, test_client_db.id)
        if client:
            session.delete(client)
            session.commit()

def test_create_contact_with_optional_fields():
    # Create a test client first
    test_client_db = Client(name="Test Client")
    with Session(engine) as session:
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)

    contact_data = {
        "name": "Test Contact",
        "email": "test@example.com",
        "phone": "1234567890",
        "position": "Manager",
        "client_id": test_client_db.id
    }

    response = test_client.post("/contacts/", json=contact_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]
    assert data["position"] == contact_data["position"]
    assert data["client_id"] == test_client_db.id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up - first delete the contact, then the client
    with Session(engine) as session:
        # First delete all contacts associated with the client
        statement = select(Contact).where(Contact.client_id == test_client_db.id)
        contacts = session.exec(statement).all()
        for contact in contacts:
            session.delete(contact)
        session.commit()

        # Then delete the client
        client = session.get(Client, test_client_db.id)
        if client:
            session.delete(client)
            session.commit()

def test_create_contact_invalid_client():
    """Test creating a contact with non-existent client"""
    contact_data = {
        "name": "Test Contact",
        "email": "test@example.com",
        "phone": "1234567890",
        "position": "Manager",
        "client_id": 999999  # Non-existent client ID
    }

    response = test_client.post("/contacts/", json=contact_data)
    assert response.status_code == 404
    assert "Client not found" in response.json()["detail"]

def test_read_contacts():
    # Create a test client
    test_client_db = Client(name="Test Client")
    with Session(engine) as session:
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id  # Store the ID for later use

        # Create test contacts
        contact1 = Contact(name="Contact 1", client_id=client_id)
        contact2 = Contact(name="Contact 2", client_id=client_id)
        session.add(contact1)
        session.add(contact2)
        session.commit()

    response = test_client.get("/contacts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(c["name"] == "Contact 1" for c in data)
    assert any(c["name"] == "Contact 2" for c in data)

    # Clean up - first delete contacts, then client
    with Session(engine) as session:
        # First delete contacts
        session.delete(contact1)
        session.delete(contact2)
        session.commit()

        # Then delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_read_contact():
    # Create a test client and contact
    with Session(engine) as session:
        test_client_db = Client(name="Test Client")
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)

        # Create a test contact
        contact = Contact(name="Test Contact", client_id=test_client_db.id)
        session.add(contact)
        session.commit()
        session.refresh(contact)
        
        # Store the IDs we need
        contact_id = contact.id
        client_id = test_client_db.id

    # Make the request
    response = test_client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Contact"
    assert data["client_id"] == client_id
    assert "created_at" in data
    assert "updated_at" in data

    # Clean up - first delete contact, then client
    with Session(engine) as session:
        # First delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()
        
        # Then delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_read_contact_not_found():
    """Test reading a non-existent contact"""
    response = test_client.get("/contacts/999999")
    assert response.status_code == 404
    assert "Contact not found" in response.json()["detail"]

def test_update_contact():
    # Create a test client
    test_client_db = Client(name="Test Client")
    with Session(engine) as session:
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id  # Store the ID for later use

        # Create a test contact
        contact = Contact(name="Test Contact", client_id=client_id)
        session.add(contact)
        session.commit()
        session.refresh(contact)
        contact_id = contact.id  # Store the ID for later use
        original_created_at = contact.created_at

    update_data = {
        "name": "Updated Contact",
        "email": "updated@example.com"
    }

    response = test_client.put(f"/contacts/{contact_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert "created_at" in data
    assert "updated_at" in data
    # Verify created_at didn't change
    assert data["created_at"] == original_created_at.isoformat()
    # Verify updated_at did change
    assert data["updated_at"] > original_created_at.isoformat()

    # Clean up - first delete contact, then client
    with Session(engine) as session:
        # First delete contact
        contact = session.get(Contact, contact_id)
        if contact:
            session.delete(contact)
            session.commit()

        # Then delete client
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_update_contact_not_found():
    """Test updating a non-existent contact"""
    update_data = {
        "name": "Updated Contact",
        "email": "updated@example.com"
    }
    response = test_client.put("/contacts/999999", json=update_data)
    assert response.status_code == 404
    assert "Contact not found" in response.json()["detail"]

def test_delete_contact():
    # Create a test client
    test_client_db = Client(name="Test Client")
    with Session(engine) as session:
        session.add(test_client_db)
        session.commit()
        session.refresh(test_client_db)
        client_id = test_client_db.id  # Store the ID for later use

        # Create a test contact
        contact = Contact(name="Test Contact", client_id=client_id)
        session.add(contact)
        session.commit()
        session.refresh(contact)
        contact_id = contact.id  # Store the ID for later use

    response = test_client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Contact deleted"}

    # Verify contact is deleted
    with Session(engine) as session:
        deleted_contact = session.get(Contact, contact_id)
        assert deleted_contact is None

    # Clean up - delete client
    with Session(engine) as session:
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

def test_delete_contact_not_found():
    """Test deleting a non-existent contact"""
    response = test_client.delete("/contacts/999999")
    assert response.status_code == 404
    assert "Contact not found" in response.json()["detail"] 
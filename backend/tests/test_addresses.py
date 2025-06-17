from fastapi.testclient import TestClient
from app.main import app
from app.models import Address, Supplier, PaymentCondition
from app.core.database import engine
from sqlmodel import Session, select

client = TestClient(app)

def test_get_addresses():
    # Create a test address
    test_address = Address(
        street="Test Street",
        exterior_number="123",
        neighborhood="Test Neighborhood",
        postal_code="12345",
        city="Test City",
        state="Test State"
    )
    with Session(engine) as session:
        session.add(test_address)
        session.commit()
        session.refresh(test_address)

    # Make the request to get all addresses
    response = client.get("/addresses/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(address["street"] == "Test Street" for address in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_address)
        session.commit()

def test_get_single_address():
    # Create a test address
    test_address = Address(
        street="Single Test Street",
        exterior_number="456",
        neighborhood="Single Test Neighborhood",
        postal_code="54321",
        city="Single Test City",
        state="Single Test State"
    )
    with Session(engine) as session:
        session.add(test_address)
        session.commit()
        session.refresh(test_address)
        address_id = test_address.id

    # Make the request to get the specific address
    response = client.get(f"/addresses/{address_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["street"] == "Single Test Street"
    assert data["id"] == address_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_address)
        session.commit()

def test_create_address():
    # Data for the new address
    new_address_data = {
        "street": "New Test Street",
        "exterior_number": "789",
        "interior_number": "A",
        "neighborhood": "New Test Neighborhood",
        "postal_code": "98765",
        "city": "New Test City",
        "state": "New Test State",
        "country": "México",
        "notes": "Test notes"
    }

    # Make the request to create an address
    response = client.post("/addresses/", json=new_address_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["street"] == "New Test Street"
    assert data["exterior_number"] == "789"
    assert data["interior_number"] == "A"
    assert data["neighborhood"] == "New Test Neighborhood"
    assert data["postal_code"] == "98765"
    assert data["city"] == "New Test City"
    assert data["state"] == "New Test State"
    assert data["country"] == "México"
    assert data["notes"] == "Test notes"
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(Address).where(Address.street == "New Test Street")
        test_address = session.exec(statement).first()
        if test_address:
            session.delete(test_address)
        session.commit()

def test_delete_address():
    # Create a test address
    test_address = Address(
        street="Delete Test Street",
        exterior_number="101",
        neighborhood="Delete Test Neighborhood",
        postal_code="10101",
        city="Delete Test City",
        state="Delete Test State"
    )
    with Session(engine) as session:
        session.add(test_address)
        session.commit()
        session.refresh(test_address)
        address_id = test_address.id

    # Make the request to delete the address
    response = client.delete(f"/addresses/{address_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Address deleted"

    # Verify the address was actually deleted
    with Session(engine) as session:
        statement = select(Address).where(Address.id == address_id)
        deleted_address = session.exec(statement).first()
        assert deleted_address is None

def test_delete_address_with_supplier():
    # Create a test payment condition
    test_payment_condition = PaymentCondition(
        name="Test Payment Condition",
        text="Test Text"
    )
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

    # Create a test address
    test_address = Address(
        street="Supplier Test Street",
        exterior_number="202",
        neighborhood="Supplier Test Neighborhood",
        postal_code="20202",
        city="Supplier Test City",
        state="Supplier Test State"
    )
    with Session(engine) as session:
        session.add(test_address)
        session.commit()
        session.refresh(test_address)

    # Create a test supplier that uses the address
    test_supplier = Supplier(
        name="Test Supplier",
        rfc="TEST123456789",
        address_id=test_address.id,
        bank_details="Test Bank Details",
        delivery_time="Test Delivery Time",
        payment_condition_id=test_payment_condition.id,
        currency="MXN"
    )
    with Session(engine) as session:
        session.add(test_supplier)
        session.commit()
        session.refresh(test_supplier)

    # Try to delete the address
    response = client.delete(f"/addresses/{test_address.id}")
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "Cannot delete address that is being used by suppliers" in data["detail"]

    # Clean up
    with Session(engine) as session:
        session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_update_address():
    # Create a test address
    test_address = Address(
        street="Test Street",
        exterior_number="123",
        interior_number="A",
        neighborhood="Test Neighborhood",
        postal_code="12345",
        city="Test City",
        state="Test State",
        country="México",
        notes="Test Notes"
    )
    with Session(engine) as session:
        session.add(test_address)
        session.commit()
        session.refresh(test_address)
        address_id = test_address.id

    # Update the address
    update_data = {
        "street": "Updated Street",
        "exterior_number": "456",
        "interior_number": "B",
        "neighborhood": "Updated Neighborhood",
        "postal_code": "54321",
        "city": "Updated City",
        "state": "Updated State",
        "country": "USA",
        "notes": "Updated Notes"
    }
    
    response = client.put(f"/addresses/{address_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == address_id
    assert data["street"] == "Updated Street"
    assert data["exterior_number"] == "456"
    assert data["interior_number"] == "B"
    assert data["neighborhood"] == "Updated Neighborhood"
    assert data["postal_code"] == "54321"
    assert data["city"] == "Updated City"
    assert data["state"] == "Updated State"
    assert data["country"] == "USA"
    assert data["notes"] == "Updated Notes"

    # Verify the database state
    with Session(engine) as session:
        db_address = session.get(Address, address_id)
        assert db_address.street == "Updated Street"
        assert db_address.exterior_number == "456"
        assert db_address.interior_number == "B"
        assert db_address.neighborhood == "Updated Neighborhood"
        assert db_address.postal_code == "54321"
        assert db_address.city == "Updated City"
        assert db_address.state == "Updated State"
        assert db_address.country == "USA"
        assert db_address.notes == "Updated Notes"

    # Clean up
    with Session(engine) as session:
        session.delete(test_address)
        session.commit()

def test_update_address_not_found():
    update_data = {
        "street": "Updated Street"
    }
    response = client.put("/addresses/999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Address not found"

def test_update_address_partial():
    # Create a test address
    test_address = Address(
        street="Test Street",
        exterior_number="123",
        interior_number="A",
        neighborhood="Test Neighborhood",
        postal_code="12345",
        city="Test City",
        state="Test State",
        country="México",
        notes="Test Notes"
    )
    with Session(engine) as session:
        session.add(test_address)
        session.commit()
        session.refresh(test_address)
        address_id = test_address.id

    # Update only some fields
    update_data = {
        "street": "Updated Street",
        "city": "Updated City"
    }
    
    response = client.put(f"/addresses/{address_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == address_id
    assert data["street"] == "Updated Street"
    assert data["city"] == "Updated City"
    # Verify other fields remain unchanged
    assert data["exterior_number"] == "123"
    assert data["interior_number"] == "A"
    assert data["neighborhood"] == "Test Neighborhood"
    assert data["postal_code"] == "12345"
    assert data["state"] == "Test State"
    assert data["country"] == "México"
    assert data["notes"] == "Test Notes"

    # Verify the database state
    with Session(engine) as session:
        db_address = session.get(Address, address_id)
        assert db_address.street == "Updated Street"
        assert db_address.city == "Updated City"
        assert db_address.exterior_number == "123"
        assert db_address.interior_number == "A"
        assert db_address.neighborhood == "Test Neighborhood"
        assert db_address.postal_code == "12345"
        assert db_address.state == "Test State"
        assert db_address.country == "México"
        assert db_address.notes == "Test Notes"

    # Clean up
    with Session(engine) as session:
        session.delete(test_address)
        session.commit() 
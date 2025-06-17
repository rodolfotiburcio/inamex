from fastapi.testclient import TestClient
from app.main import app
from app.models import Supplier, PaymentCondition, Address
from app.core.database import engine
from sqlmodel import Session, select

client = TestClient(app)

def test_get_suppliers():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(name="Test Payment Condition", text="Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Create a test supplier
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

    # Make the request to get all suppliers
    response = client.get("/suppliers/")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(supplier["name"] == "Test Supplier" for supplier in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_get_single_supplier():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(
        name="Single Test Payment Condition",
        text="Single Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Create a test supplier
    test_supplier = Supplier(
        name="Single Test Supplier",
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
        supplier_id = test_supplier.id

    # Make the request to get the specific supplier
    response = client.get(f"/suppliers/{supplier_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Test Supplier"
    assert data["id"] == supplier_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_create_supplier():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(
        name="Create Test Payment Condition",
        text="Create Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Data for the new supplier
    new_supplier_data = {
        "name": "New Test Supplier",
        "rfc": "TEST123456789",
        "address_id": test_address.id,
        "bank_details": "Test Bank Details",
        "delivery_time": "Test Delivery Time",
        "payment_condition_id": test_payment_condition.id,
        "currency": "MXN",
        "notes": "Test Notes"
    }

    # Make the request to create a supplier
    response = client.post("/suppliers/", json=new_supplier_data)
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Test Supplier"
    assert data["address_id"] == test_address.id
    assert data["bank_details"] == "Test Bank Details"
    assert data["delivery_time"] == "Test Delivery Time"
    assert data["payment_condition_id"] == test_payment_condition.id
    assert data["currency"] == "MXN"
    assert data["notes"] == "Test Notes"
    assert "id" in data

    # Clean up
    with Session(engine) as session:
        statement = select(Supplier).where(Supplier.name == "New Test Supplier")
        test_supplier = session.exec(statement).first()
        if test_supplier:
            session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_delete_supplier():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(
        name="Delete Test Payment Condition",
        text="Delete Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Create a test supplier
    test_supplier = Supplier(
        name="Supplier To Delete",
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
        supplier_id = test_supplier.id

    # Make the request to delete the supplier
    response = client.delete(f"/suppliers/{supplier_id}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Supplier deleted"

    # Verify the supplier was actually deleted
    with Session(engine) as session:
        statement = select(Supplier).where(Supplier.id == supplier_id)
        deleted_supplier = session.exec(statement).first()
        assert deleted_supplier is None

    # Clean up
    with Session(engine) as session:
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_update_supplier():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(
        name="Update Test Payment Condition",
        text="Update Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Create a test supplier
    test_supplier = Supplier(
        name="Supplier To Update",
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
        supplier_id = test_supplier.id

    # Update the supplier
    update_data = {
        "name": "Updated Supplier",
        "rfc": "TEST123456789",
        "bank_details": "Updated Bank Details",
        "delivery_time": "Updated Delivery Time",
        "currency": "USD",
        "notes": "Updated Notes"
    }
    
    response = client.put(f"/suppliers/{supplier_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == supplier_id
    assert data["name"] == "Updated Supplier"
    assert data["bank_details"] == "Updated Bank Details"
    assert data["delivery_time"] == "Updated Delivery Time"
    assert data["currency"] == "USD"
    assert data["notes"] == "Updated Notes"
    # Verify other fields remain unchanged
    assert data["address_id"] == test_address.id
    assert data["payment_condition_id"] == test_payment_condition.id

    # Verify the database state
    with Session(engine) as session:
        db_supplier = session.get(Supplier, supplier_id)
        assert db_supplier.name == "Updated Supplier"
        assert db_supplier.bank_details == "Updated Bank Details"
        assert db_supplier.delivery_time == "Updated Delivery Time"
        assert db_supplier.currency == "USD"
        assert db_supplier.notes == "Updated Notes"
        assert db_supplier.address_id == test_address.id
        assert db_supplier.payment_condition_id == test_payment_condition.id

    # Clean up
    with Session(engine) as session:
        session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_update_supplier_not_found():
    update_data = {
        "name": "Updated Supplier"
    }
    response = client.put("/suppliers/999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"

def test_update_supplier_invalid_address():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(
        name="Invalid Address Test Payment Condition",
        text="Invalid Address Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Create a test supplier
    test_supplier = Supplier(
        name="Invalid Address Test Supplier",
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
        supplier_id = test_supplier.id

    # Try to update with invalid address_id
    update_data = {
        "address_id": 999
    }
    response = client.put(f"/suppliers/{supplier_id}", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Address not found"

    # Clean up
    with Session(engine) as session:
        session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit()

def test_update_supplier_invalid_payment_condition():
    # Create a test payment condition first
    test_payment_condition = PaymentCondition(
        name="Invalid Payment Condition Test Payment Condition",
        text="Invalid Payment Condition Test Text")
    with Session(engine) as session:
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)

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

    # Create a test supplier
    test_supplier = Supplier(
        name="Invalid Payment Condition Test Supplier",
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
        supplier_id = test_supplier.id

    # Try to update with invalid payment_condition_id
    update_data = {
        "payment_condition_id": 999
    }
    response = client.put(f"/suppliers/{supplier_id}", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Payment condition not found"

    # Clean up
    with Session(engine) as session:
        session.delete(test_supplier)
        session.delete(test_address)
        session.delete(test_payment_condition)
        session.commit() 
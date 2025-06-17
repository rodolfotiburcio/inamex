from fastapi.testclient import TestClient
from app.main import app
from app.models import (
    Order, OrderCreate, OrderResponse,
    Supplier, PaymentCondition, Address,
    OrderStatus, User, ArticleOrderStatus, ArticleOrder, OrderWithArticlesCreate
)
from app.core.database import engine
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime

client = TestClient(app)

def create_test_dependencies():
    """Helper function to create required related entities"""
    # Create test address first (needed by supplier)
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
    
    # Create test payment condition
    test_payment_condition = PaymentCondition(
        name="Test Payment Condition",
        description="Test Description",
        text="Test Text",
        active=True
    )
    
    # Create test supplier
    test_supplier = Supplier(
        name="Test Supplier",
        rfc="TEST123456789",
        address_id=test_address.id,  # Will be set after address is created
        bank_details="Test Bank Details",
        delivery_time="30 days",
        payment_condition_id=test_payment_condition.id,  # Will be set after payment condition is created
        currency="USD",
        notes="Test Notes"
    )
    
    # Create test order status
    test_order_status = OrderStatus(
        name="Test Order Status",
        description="Test Description",
        order=1,
        active=True
    )
    
    # Create test users
    test_user1 = User(
        username="test_user1",
        full_name="Test User 1",
        password_hash="hashed_password1"
    )
    test_user2 = User(
        username="test_user2",
        full_name="Test User 2",
        password_hash="hashed_password2"
    )
    test_user3 = User(
        username="test_user3",
        full_name="Test User 3",
        password_hash="hashed_password3"
    )
    test_user4 = User(
        username="test_user4",
        full_name="Test User 4",
        password_hash="hashed_password4"
    )
    
    with Session(engine) as session:
        # Add address first
        session.add(test_address)
        session.commit()
        session.refresh(test_address)
        
        # Add payment condition
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)
        
        # Now add supplier with the correct IDs
        test_supplier.address_id = test_address.id
        test_supplier.payment_condition_id = test_payment_condition.id
        session.add(test_supplier)
        session.commit()
        session.refresh(test_supplier)
        
        # Add order status
        session.add(test_order_status)
        session.commit()
        session.refresh(test_order_status)
        
        # Add users
        session.add(test_user1)
        session.add(test_user2)
        session.add(test_user3)
        session.add(test_user4)
        session.commit()
        session.refresh(test_user1)
        session.refresh(test_user2)
        session.refresh(test_user3)
        session.refresh(test_user4)
        
        return (
            test_supplier.id,
            test_payment_condition.id,
            test_address.id,
            test_order_status.id,
            test_user1.id,
            test_user2.id,
            test_user3.id,
            test_user4.id
        )

def cleanup_test_dependencies(
    supplier_id, payment_condition_id, address_id,
    order_status_id, user1_id, user2_id, user3_id, user4_id
):
    """Helper function to clean up related entities"""
    with Session(engine) as session:
        # First delete all orders to avoid foreign key constraints
        orders = session.exec(select(Order)).all()
        for order in orders:
            session.delete(order)
        session.commit()
        
        # Then delete the rest of the entities
        supplier = session.get(Supplier, supplier_id)
        if supplier:
            session.delete(supplier)
            
        payment_condition = session.get(PaymentCondition, payment_condition_id)
        if payment_condition:
            session.delete(payment_condition)
            
        address = session.get(Address, address_id)
        if address:
            session.delete(address)
            
        order_status = session.get(OrderStatus, order_status_id)
        if order_status:
            session.delete(order_status)
            
        user1 = session.get(User, user1_id)
        if user1:
            session.delete(user1)
            
        user2 = session.get(User, user2_id)
        if user2:
            session.delete(user2)
            
        user3 = session.get(User, user3_id)
        if user3:
            session.delete(user3)
            
        user4 = session.get(User, user4_id)
        if user4:
            session.delete(user4)
            
        session.commit()

def test_get_orders():
    # Create dependencies
    (
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()
    
    # Create a test order
    test_order = Order(
        supplier_id=supplier_id,
        address="Test Address",
        bank_details="Test Bank Details",
        delivery_time="30 days",
        payment_condition_id=payment_condition_id,
        currency="USD",
        subtotal=Decimal("100.00"),
        vat=Decimal("19.00"),
        discount=Decimal("0.00"),
        total=Decimal("119.00"),
        shipping_address_id=address_id,
        status_id=order_status_id,
        acceptance_id=user1_id,
        requested_by_id=user2_id,
        reviewed_by_id=user3_id,
        approved_by_id=user4_id
    )
    
    with Session(engine) as session:
        session.add(test_order)
        session.commit()
        session.refresh(test_order)

    # Make request
    response = client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(order["supplier_id"] == supplier_id for order in data)

    # Clean up
    with Session(engine) as session:
        session.delete(test_order)
        session.commit()
    cleanup_test_dependencies(
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_get_single_order():
    # Create dependencies
    (
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()
    
    # Create a test order
    test_order = Order(
        supplier_id=supplier_id,
        address="Test Address",
        bank_details="Test Bank Details",
        delivery_time="30 days",
        payment_condition_id=payment_condition_id,
        currency="USD",
        subtotal=Decimal("100.00"),
        vat=Decimal("19.00"),
        discount=Decimal("0.00"),
        total=Decimal("119.00"),
        shipping_address_id=address_id,
        status_id=order_status_id,
        acceptance_id=user1_id,
        requested_by_id=user2_id,
        reviewed_by_id=user3_id,
        approved_by_id=user4_id
    )
    
    with Session(engine) as session:
        session.add(test_order)
        session.commit()
        session.refresh(test_order)
        order_id = test_order.id

    # Make request
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["supplier_id"] == supplier_id
    assert data["address"] == "Test Address"
    assert data["bank_details"] == "Test Bank Details"
    assert data["delivery_time"] == "30 days"
    assert data["payment_condition_id"] == payment_condition_id
    assert data["currency"] == "USD"
    assert data["subtotal"] == "100.00"
    assert data["vat"] == "19.00"
    assert data["discount"] == "0.00"
    assert data["total"] == "119.00"
    assert data["shipping_address_id"] == address_id
    assert data["status_id"] == order_status_id
    assert data["acceptance_id"] == user1_id
    assert data["requested_by_id"] == user2_id
    assert data["reviewed_by_id"] == user3_id
    assert data["approved_by_id"] == user4_id

    # Clean up
    with Session(engine) as session:
        session.delete(test_order)
        session.commit()
    cleanup_test_dependencies(
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_create_order():
    # Create dependencies
    (
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()
    
    # Data for the new order
    new_order_data = {
        "supplier_id": supplier_id,
        "address": "New Test Address",
        "bank_details": "New Test Bank Details",
        "delivery_time": "45 days",
        "payment_condition_id": payment_condition_id,
        "currency": "EUR",
        "subtotal": "200.00",
        "vat": "38.00",
        "discount": "10.00",
        "total": "228.00",
        "shipping_address_id": address_id,
        "status_id": order_status_id,
        "acceptance_id": user1_id,
        "requested_by_id": user2_id,
        "reviewed_by_id": user3_id,
        "approved_by_id": user4_id
    }

    # Make request
    response = client.post("/orders/", json=new_order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["supplier_id"] == supplier_id
    assert data["address"] == "New Test Address"
    assert data["bank_details"] == "New Test Bank Details"
    assert data["delivery_time"] == "45 days"
    assert data["payment_condition_id"] == payment_condition_id
    assert data["currency"] == "EUR"
    assert data["subtotal"] == "200.00"
    assert data["vat"] == "38.00"
    assert data["discount"] == "10.00"
    assert data["total"] == "228.00"
    assert data["shipping_address_id"] == address_id
    assert data["status_id"] == order_status_id
    assert data["acceptance_id"] == user1_id
    assert data["requested_by_id"] == user2_id
    assert data["reviewed_by_id"] == user3_id
    assert data["approved_by_id"] == user4_id

    # Clean up
    with Session(engine) as session:
        statement = select(Order).where(Order.address == "New Test Address")
        test_order = session.exec(statement).first()
        if test_order:
            session.delete(test_order)
            session.commit()
    cleanup_test_dependencies(
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_create_order_invalid_references():
    """Test creating an order with invalid foreign keys"""
    # Try to create an order with non-existent references
    new_order_data = {
        "supplier_id": 99999,  # Non-existent supplier
        "address": "Test Address",
        "bank_details": "Test Bank Details",
        "delivery_time": "30 days",
        "payment_condition_id": 99999,  # Non-existent payment condition
        "currency": "USD",
        "subtotal": "100.00",
        "vat": "19.00",
        "discount": "0.00",
        "total": "119.00",
        "shipping_address_id": 99999,  # Non-existent address
        "status_id": 99999,  # Non-existent status
        "acceptance_id": 99999,  # Non-existent user
        "requested_by_id": 99999,  # Non-existent user
        "reviewed_by_id": 99999,  # Non-existent user
        "approved_by_id": 99999  # Non-existent user
    }

    # Make request
    response = client.post("/orders/", json=new_order_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data  # Should contain error message

def test_delete_order():
    # Create dependencies
    (
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()
    
    # Create a test order
    test_order = Order(
        supplier_id=supplier_id,
        address="Order to Delete",
        bank_details="Test Bank Details",
        delivery_time="30 days",
        payment_condition_id=payment_condition_id,
        currency="USD",
        subtotal=Decimal("100.00"),
        vat=Decimal("19.00"),
        discount=Decimal("0.00"),
        total=Decimal("119.00"),
        shipping_address_id=address_id,
        status_id=order_status_id,
        acceptance_id=user1_id,
        requested_by_id=user2_id,
        reviewed_by_id=user3_id,
        approved_by_id=user4_id
    )
    
    with Session(engine) as session:
        session.add(test_order)
        session.commit()
        session.refresh(test_order)
        order_id = test_order.id

    # Make request
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Order deleted"

    # Verify deletion
    with Session(engine) as session:
        statement = select(Order).where(Order.id == order_id)
        deleted_order = session.exec(statement).first()
        assert deleted_order is None
    
    # Clean up dependencies
    cleanup_test_dependencies(
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_delete_nonexistent_order():
    response = client.delete("/orders/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_update_order():
    """Test updating an order"""
    # Create dependencies
    with Session(engine) as session:
        # Create address first
        address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="Test Country"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        address_id = address.id

        # Create payment condition
        payment_condition = PaymentCondition(
            name="Test Payment Condition",
            description="Test Description",
            text="Test Text"
        )
        session.add(payment_condition)
        session.commit()
        session.refresh(payment_condition)
        payment_condition_id = payment_condition.id

        # Create supplier with the address and payment condition
        supplier = Supplier(
            name="Test Supplier",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="1 week",
            payment_condition_id=payment_condition_id,
            currency="USD",
            notes="Test Notes"
        )
        session.add(supplier)
        session.commit()
        session.refresh(supplier)
        supplier_id = supplier.id

        # Create shipping address
        shipping_address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="Test Country"
        )
        session.add(shipping_address)
        session.commit()
        session.refresh(shipping_address)
        shipping_address_id = shipping_address.id

        # Create order status
        order_status = OrderStatus(
            name="Test Status",
            description="Test Description"
        )
        session.add(order_status)
        session.commit()
        session.refresh(order_status)
        status_id = order_status.id

        # Create users
        acceptance_user = User(
            username="acceptance_user",
            full_name="Acceptance User",
            password_hash="hashed_password"
        )
        session.add(acceptance_user)
        session.commit()
        session.refresh(acceptance_user)
        acceptance_id = acceptance_user.id

        requested_by_user = User(
            username="requested_user",
            full_name="Requested User",
            password_hash="hashed_password"
        )
        session.add(requested_by_user)
        session.commit()
        session.refresh(requested_by_user)
        requested_by_id = requested_by_user.id

        reviewed_by_user = User(
            username="reviewed_user",
            full_name="Reviewed User",
            password_hash="hashed_password"
        )
        session.add(reviewed_by_user)
        session.commit()
        session.refresh(reviewed_by_user)
        reviewed_by_id = reviewed_by_user.id

        approved_by_user = User(
            username="approved_user",
            full_name="Approved User",
            password_hash="hashed_password"
        )
        session.add(approved_by_user)
        session.commit()
        session.refresh(approved_by_user)
        approved_by_id = approved_by_user.id

        # Create order
        order = Order(
            supplier_id=supplier_id,
            address="Test Address",
            bank_details="Test Bank Details",
            date=datetime.utcnow(),
            delivery_time="1 week",
            payment_condition_id=payment_condition_id,
            currency="USD",
            supplier_reference="Test Reference",
            acceptance_id=acceptance_id,
            requested_by_id=requested_by_id,
            reviewed_by_id=reviewed_by_id,
            approved_by_id=approved_by_id,
            subtotal=Decimal("100.00"),
            vat=Decimal("16.00"),
            discount=Decimal("0.00"),
            total=Decimal("116.00"),
            notes="Test Notes",
            shipping_address_id=shipping_address_id,
            status_id=status_id
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        order_id = order.id

    # Update order
    update_data = {
        "address": "Updated Address",
        "bank_details": "Updated Bank Details",
        "delivery_time": "2 weeks",
        "currency": "EUR",
        "supplier_reference": "Updated Reference",
        "notes": "Updated Notes",
        "subtotal": "200.00",
        "vat": "32.00",
        "discount": "10.00",
        "total": "222.00"
    }
    response = client.put(f"/orders/{order_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["address"] == "Updated Address"
    assert data["bank_details"] == "Updated Bank Details"
    assert data["delivery_time"] == "2 weeks"
    assert data["currency"] == "EUR"
    assert data["supplier_reference"] == "Updated Reference"
    assert data["notes"] == "Updated Notes"
    assert data["subtotal"] == "200.00"
    assert data["vat"] == "32.00"
    assert data["discount"] == "10.00"
    assert data["total"] == "222.00"

    # Verify database state
    with Session(engine) as session:
        statement = select(Order).where(Order.id == order_id)
        result = session.exec(statement)
        updated_order = result.one_or_none()
        assert updated_order is not None
        assert updated_order.address == "Updated Address"
        assert updated_order.bank_details == "Updated Bank Details"
        assert updated_order.delivery_time == "2 weeks"
        assert updated_order.currency == "EUR"
        assert updated_order.supplier_reference == "Updated Reference"
        assert updated_order.notes == "Updated Notes"
        assert updated_order.subtotal == Decimal("200.00")
        assert updated_order.vat == Decimal("32.00")
        assert updated_order.discount == Decimal("10.00")
        assert updated_order.total == Decimal("222.00")

    # Cleanup
    with Session(engine) as session:
        # Delete order
        session.delete(updated_order)
        session.commit()

        # Delete users
        session.delete(acceptance_user)
        session.delete(requested_by_user)
        session.delete(reviewed_by_user)
        session.delete(approved_by_user)
        session.commit()

        # Delete status
        session.delete(order_status)
        session.commit()

        # Delete shipping address
        session.delete(shipping_address)
        session.commit()

        # Delete supplier
        session.delete(supplier)
        session.commit()

        # Delete payment condition
        session.delete(payment_condition)
        session.commit()

        # Delete address
        session.delete(address)
        session.commit()

def test_update_order_not_found():
    """Test updating a non-existent order"""
    update_data = {
        "address": "Updated Address"
    }
    response = client.put("/orders/999999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_update_order_invalid_supplier():
    """Test updating an order with an invalid supplier"""
    # Create dependencies
    with Session(engine) as session:
        # Create address first
        address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="Test Country"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        address_id = address.id

        # Create payment condition
        payment_condition = PaymentCondition(
            name="Test Payment Condition",
            description="Test Description",
            text="Test Text"
        )
        session.add(payment_condition)
        session.commit()
        session.refresh(payment_condition)
        payment_condition_id = payment_condition.id

        # Create supplier
        supplier = Supplier(
            name="Test Supplier",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="1 week",
            payment_condition_id=payment_condition_id,
            currency="USD",
            notes="Test Notes"
        )
        session.add(supplier)
        session.commit()
        session.refresh(supplier)
        supplier_id = supplier.id

        # Create shipping address
        shipping_address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="Test Country"
        )
        session.add(shipping_address)
        session.commit()
        session.refresh(shipping_address)
        shipping_address_id = shipping_address.id

        # Create order status
        order_status = OrderStatus(
            name="Test Status",
            description="Test Description"
        )
        session.add(order_status)
        session.commit()
        session.refresh(order_status)
        status_id = order_status.id

        # Create user
        user = User(
            username="test_user",
            full_name="Test User",
            password_hash="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

        # Create order with valid supplier
        order = Order(
            supplier_id=supplier_id,
            address="Test Address",
            bank_details="Test Bank Details",
            date=datetime.utcnow(),
            delivery_time="1 week",
            payment_condition_id=payment_condition_id,
            currency="USD",
            supplier_reference="Test Reference",
            acceptance_id=user_id,
            requested_by_id=user_id,
            reviewed_by_id=user_id,
            approved_by_id=user_id,
            subtotal=Decimal("100.00"),
            vat=Decimal("16.00"),
            discount=Decimal("0.00"),
            total=Decimal("116.00"),
            notes="Test Notes",
            shipping_address_id=shipping_address_id,
            status_id=status_id
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        order_id = order.id

    # Try to update order with invalid supplier
    update_data = {
        "supplier_id": 999999
    }
    response = client.put(f"/orders/{order_id}", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Supplier not found"

    # Cleanup
    with Session(engine) as session:
        # Delete order
        session.delete(order)
        session.commit()

        # Delete user
        session.delete(user)
        session.commit()

        # Delete status
        session.delete(order_status)
        session.commit()

        # Delete shipping address
        session.delete(shipping_address)
        session.commit()

        # Delete supplier
        session.delete(supplier)
        session.commit()

        # Delete payment condition
        session.delete(payment_condition)
        session.commit()

        # Delete address
        session.delete(address)
        session.commit()

def test_update_order_partial():
    """Test partial update of an order"""
    # Create dependencies
    with Session(engine) as session:
        # Create address first
        address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="Test Country"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        address_id = address.id

        # Create payment condition
        payment_condition = PaymentCondition(
            name="Test Payment Condition",
            description="Test Description",
            text="Test Text"
        )
        session.add(payment_condition)
        session.commit()
        session.refresh(payment_condition)
        payment_condition_id = payment_condition.id

        # Create supplier
        supplier = Supplier(
            name="Test Supplier",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="1 week",
            payment_condition_id=payment_condition_id,
            currency="USD",
            notes="Test Notes"
        )
        session.add(supplier)
        session.commit()
        session.refresh(supplier)
        supplier_id = supplier.id

        # Create shipping address
        shipping_address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="Test Country"
        )
        session.add(shipping_address)
        session.commit()
        session.refresh(shipping_address)
        shipping_address_id = shipping_address.id

        # Create order status
        order_status = OrderStatus(
            name="Test Status",
            description="Test Description"
        )
        session.add(order_status)
        session.commit()
        session.refresh(order_status)
        status_id = order_status.id

        # Create user
        user = User(
            username="test_user",
            full_name="Test User",
            password_hash="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

        # Create order
        order = Order(
            supplier_id=supplier_id,
            address="Test Address",
            bank_details="Test Bank Details",
            date=datetime.utcnow(),
            delivery_time="1 week",
            payment_condition_id=payment_condition_id,
            currency="USD",
            supplier_reference="Test Reference",
            acceptance_id=user_id,
            requested_by_id=user_id,
            reviewed_by_id=user_id,
            approved_by_id=user_id,
            subtotal=Decimal("100.00"),
            vat=Decimal("16.00"),
            discount=Decimal("0.00"),
            total=Decimal("116.00"),
            notes="Test Notes",
            shipping_address_id=shipping_address_id,
            status_id=status_id
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        order_id = order.id

    # Update only some fields
    update_data = {
        "address": "Updated Address",
        "notes": "Updated Notes"
    }
    response = client.put(f"/orders/{order_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["address"] == "Updated Address"
    assert data["notes"] == "Updated Notes"
    # Verify other fields remain unchanged
    assert data["bank_details"] == "Test Bank Details"
    assert data["delivery_time"] == "1 week"
    assert data["currency"] == "USD"
    assert data["supplier_reference"] == "Test Reference"
    assert data["subtotal"] == "100.00"
    assert data["vat"] == "16.00"
    assert data["discount"] == "0.00"
    assert data["total"] == "116.00"

    # Verify database state
    with Session(engine) as session:
        statement = select(Order).where(Order.id == order_id)
        result = session.exec(statement)
        updated_order = result.one_or_none()
        assert updated_order is not None
        assert updated_order.address == "Updated Address"
        assert updated_order.notes == "Updated Notes"
        # Verify other fields remain unchanged
        assert updated_order.bank_details == "Test Bank Details"
        assert updated_order.delivery_time == "1 week"
        assert updated_order.currency == "USD"
        assert updated_order.supplier_reference == "Test Reference"
        assert updated_order.subtotal == Decimal("100.00")
        assert updated_order.vat == Decimal("16.00")
        assert updated_order.discount == Decimal("0.00")
        assert updated_order.total == Decimal("116.00")

    # Cleanup
    with Session(engine) as session:
        # Delete order
        session.delete(updated_order)
        session.commit()

        # Delete user
        session.delete(user)
        session.commit()

        # Delete status
        session.delete(order_status)
        session.commit()

        # Delete shipping address
        session.delete(shipping_address)
        session.commit()

        # Delete supplier
        session.delete(supplier)
        session.commit()

        # Delete payment condition
        session.delete(payment_condition)
        session.commit()

        # Delete address
        session.delete(address)
        session.commit()

def test_create_order_with_articles():
    """Test creating an order with its article orders"""
    # Create dependencies
    (
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Create test article order status
    with Session(engine) as session:
        test_article_order_status = ArticleOrderStatus(
            name="Test Article Order Status",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_article_order_status)
        session.commit()
        session.refresh(test_article_order_status)
        article_order_status_id = test_article_order_status.id

    # Data for creating an order with article orders
    order_data = {
        "order": {
            "supplier_id": supplier_id,
            "address": "Test Address",
            "bank_details": "Test Bank Details",
            "delivery_time": "30 days",
            "payment_condition_id": payment_condition_id,
            "currency": "USD",
            "subtotal": "100.00",
            "vat": "19.00",
            "discount": "0.00",
            "total": "119.00",
            "shipping_address_id": address_id,
            "status_id": order_status_id,
            "acceptance_id": user1_id,
            "requested_by_id": user2_id,
            "reviewed_by_id": user3_id,
            "approved_by_id": user4_id
        },
        "articles": [
            {
                "article_req_id": None,
                "status_id": article_order_status_id,
                "position": 1,
                "quantity": "10.00",
                "unit": "pcs",
                "brand": "Test Brand 1",
                "model": "Test Model 1",
                "unit_price": "10.00",
                "total": "100.00",
                "notes": "Test Notes 1"
            },
            {
                "article_req_id": None,
                "status_id": article_order_status_id,
                "position": 2,
                "quantity": "5.00",
                "unit": "kg",
                "brand": "Test Brand 2",
                "model": "Test Model 2",
                "unit_price": "3.80",
                "total": "19.00",
                "notes": "Test Notes 2"
            }
        ]
    }

    # Make request
    response = client.post("/orders/with-articles", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["supplier_id"] == supplier_id
    assert data["address"] == "Test Address"
    assert data["bank_details"] == "Test Bank Details"
    assert data["delivery_time"] == "30 days"
    assert data["payment_condition_id"] == payment_condition_id
    assert data["currency"] == "USD"
    assert data["subtotal"] == "100.00"
    assert data["vat"] == "19.00"
    assert data["discount"] == "0.00"
    assert data["total"] == "119.00"
    assert data["shipping_address_id"] == address_id
    assert data["status_id"] == order_status_id
    assert data["acceptance_id"] == user1_id
    assert data["requested_by_id"] == user2_id
    assert data["reviewed_by_id"] == user3_id
    assert data["approved_by_id"] == user4_id

    # Verify that the article orders were created and linked to the order
    with Session(engine) as session:
        order = session.get(Order, data["id"])
        assert order is not None
        
        statement = select(ArticleOrder).where(ArticleOrder.order_id == order.id)
        result = session.exec(statement)
        article_orders = result.all()
        assert len(article_orders) == 2
        
        # Verify first article order
        assert article_orders[0].position == 1
        assert article_orders[0].quantity == Decimal("10.00")
        assert article_orders[0].unit == "pcs"
        assert article_orders[0].brand == "Test Brand 1"
        assert article_orders[0].model == "Test Model 1"
        assert article_orders[0].unit_price == Decimal("10.00")
        assert article_orders[0].total == Decimal("100.00")
        assert article_orders[0].notes == "Test Notes 1"
        
        # Verify second article order
        assert article_orders[1].position == 2
        assert article_orders[1].quantity == Decimal("5.00")
        assert article_orders[1].unit == "kg"
        assert article_orders[1].brand == "Test Brand 2"
        assert article_orders[1].model == "Test Model 2"
        assert article_orders[1].unit_price == Decimal("3.80")
        assert article_orders[1].total == Decimal("19.00")
        assert article_orders[1].notes == "Test Notes 2"
        
        # Clean up
        for article_order in article_orders:
            session.delete(article_order)
        session.delete(order)
        session.delete(test_article_order_status)
        session.commit()

    # Clean up dependencies
    cleanup_test_dependencies(
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_create_order_with_articles_invalid_references():
    """Test creating an order with article orders using invalid references"""
    # Create dependencies
    (
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Create test article order status
    with Session(engine) as session:
        test_article_order_status = ArticleOrderStatus(
            name="Test Article Order Status",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_article_order_status)
        session.commit()
        session.refresh(test_article_order_status)
        article_order_status_id = test_article_order_status.id

    # Data for creating an order with article orders using invalid references
    order_data = {
        "order": {
            "supplier_id": 99999,  # Invalid supplier_id
            "address": "Test Address",
            "bank_details": "Test Bank Details",
            "delivery_time": "30 days",
            "payment_condition_id": payment_condition_id,
            "currency": "USD",
            "subtotal": "100.00",
            "vat": "19.00",
            "discount": "0.00",
            "total": "119.00",
            "shipping_address_id": address_id,
            "status_id": order_status_id,
            "acceptance_id": user1_id,
            "requested_by_id": user2_id,
            "reviewed_by_id": user3_id,
            "approved_by_id": user4_id
        },
        "articles": [
            {
                "article_req_id": None,
                "status_id": 99999,  # Invalid article order status_id
                "position": 1,
                "quantity": "10.00",
                "unit": "pcs",
                "brand": "Test Brand",
                "model": "Test Model",
                "unit_price": "10.00",
                "total": "100.00"
            }
        ]
    }

    # Make request
    response = client.post("/orders/with-articles", json=order_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "invalid" in data["detail"].lower()

    # Clean up
    with Session(engine) as session:
        session.delete(test_article_order_status)
        session.commit()

    # Clean up dependencies
    cleanup_test_dependencies(
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) 
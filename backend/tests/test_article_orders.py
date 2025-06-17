from fastapi.testclient import TestClient
from app.main import app
from app.models import (
    ArticleOrder, Order, Article, ArticleOrderStatus,
    Supplier, PaymentCondition, Address, OrderStatus, User, ArticleState
)
from app.core.database import engine
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime

client = TestClient(app)

def create_test_dependencies():
    """Create necessary test dependencies and return their IDs"""
    with Session(engine) as session:
        # Create test address
        test_address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="México"
        )
        session.add(test_address)
        session.commit()
        session.refresh(test_address)
        address_id = test_address.id

        # Create test payment condition
        test_payment_condition = PaymentCondition(
            name="Test Payment Condition",
            description="Test Description",
            text="Test Text",
            active=True
        )
        session.add(test_payment_condition)
        session.commit()
        session.refresh(test_payment_condition)
        payment_condition_id = test_payment_condition.id

        # Create test supplier
        test_supplier = Supplier(
            name="Test Supplier",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="30 days",
            payment_condition_id=payment_condition_id,
            currency="USD"
        )
        session.add(test_supplier)
        session.commit()
        session.refresh(test_supplier)
        supplier_id = test_supplier.id

        # Create test order status
        test_order_status = OrderStatus(
            name="Test Order Status",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_order_status)
        session.commit()
        session.refresh(test_order_status)
        order_status_id = test_order_status.id

        # Create test article order status
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

        # Create test users
        test_user1 = User(
            username="testuser1",
            full_name="Test User 1",
            password_hash="hashedpassword1"
        )
        test_user2 = User(
            username="testuser2",
            full_name="Test User 2",
            password_hash="hashedpassword2"
        )
        test_user3 = User(
            username="testuser3",
            full_name="Test User 3",
            password_hash="hashedpassword3"
        )
        test_user4 = User(
            username="testuser4",
            full_name="Test User 4",
            password_hash="hashedpassword4"
        )
        session.add(test_user1)
        session.add(test_user2)
        session.add(test_user3)
        session.add(test_user4)
        session.commit()
        session.refresh(test_user1)
        session.refresh(test_user2)
        session.refresh(test_user3)
        session.refresh(test_user4)
        user1_id = test_user1.id
        user2_id = test_user2.id
        user3_id = test_user3.id
        user4_id = test_user4.id

        # Create test order
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
        session.add(test_order)
        session.commit()
        session.refresh(test_order)
        order_id = test_order.id

        # Create test article state
        test_article_state = ArticleState(
            name="Test Article State",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(test_article_state)
        session.commit()
        session.refresh(test_article_state)
        article_state_id = test_article_state.id

        # Create test article
        test_article = Article(
            requirement_id=None,
            quantity=Decimal("10.5"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x20x30",
            state_id=article_state_id
        )
        session.add(test_article)
        session.commit()
        session.refresh(test_article)
        article_id = test_article.id

        return (
            order_id, article_id, article_order_status_id,
            supplier_id, payment_condition_id, address_id,
            order_status_id, user1_id, user2_id, user3_id, user4_id
        )

def cleanup_test_dependencies(
    order_id, article_id, article_order_status_id,
    supplier_id, payment_condition_id, address_id,
    order_status_id, user1_id, user2_id, user3_id, user4_id
):
    """Clean up test dependencies"""
    with Session(engine) as session:
        # Delete article order first
        statement = select(ArticleOrder).where(ArticleOrder.order_id == order_id)
        article_orders = session.exec(statement).all()
        for article_order in article_orders:
            session.delete(article_order)

        # Delete order
        statement = select(Order).where(Order.id == order_id)
        order = session.exec(statement).first()
        if order:
            session.delete(order)

        # Delete article
        statement = select(Article).where(Article.id == article_id)
        article = session.exec(statement).first()
        if article:
            session.delete(article)

        # Delete article state
        statement = select(ArticleState).where(ArticleState.id == article.state_id)
        article_state = session.exec(statement).first()
        if article_state:
            session.delete(article_state)

        # Delete article order status
        statement = select(ArticleOrderStatus).where(ArticleOrderStatus.id == article_order_status_id)
        article_order_status = session.exec(statement).first()
        if article_order_status:
            session.delete(article_order_status)

        # Delete supplier
        statement = select(Supplier).where(Supplier.id == supplier_id)
        supplier = session.exec(statement).first()
        if supplier:
            session.delete(supplier)

        # Delete payment condition
        statement = select(PaymentCondition).where(PaymentCondition.id == payment_condition_id)
        payment_condition = session.exec(statement).first()
        if payment_condition:
            session.delete(payment_condition)

        # Delete address
        statement = select(Address).where(Address.id == address_id)
        address = session.exec(statement).first()
        if address:
            session.delete(address)

        # Delete order status
        statement = select(OrderStatus).where(OrderStatus.id == order_status_id)
        order_status = session.exec(statement).first()
        if order_status:
            session.delete(order_status)

        # Delete users
        for user_id in [user1_id, user2_id, user3_id, user4_id]:
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()
            if user:
                session.delete(user)

        session.commit()

def test_get_article_orders():
    # Create dependencies
    (
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Create test article order
    test_article_order = ArticleOrder(
        order_id=order_id,
        article_req_id=article_id,
        status_id=article_order_status_id,
        position=1,
        quantity=Decimal("10.5"),
        unit="pcs",
        brand="Test Brand",
        model="Test Model",
        unit_price=Decimal("100.00"),
        total=Decimal("1050.00"),
        notes="Test notes"
    )
    with Session(engine) as session:
        session.add(test_article_order)
        session.commit()
        session.refresh(test_article_order)

    # Make request
    response = client.get("/article-orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(
        article_order["order_id"] == order_id and
        article_order["article_req_id"] == article_id
        for article_order in data
    )

    # Clean up
    with Session(engine) as session:
        session.delete(test_article_order)
        session.commit()
    cleanup_test_dependencies(
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_get_single_article_order():
    # Create dependencies
    (
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Create test article order
    test_article_order = ArticleOrder(
        order_id=order_id,
        article_req_id=article_id,
        status_id=article_order_status_id,
        position=1,
        quantity=Decimal("10.5"),
        unit="pcs",
        brand="Test Brand",
        model="Test Model",
        unit_price=Decimal("100.00"),
        total=Decimal("1050.00"),
        notes="Test notes"
    )
    with Session(engine) as session:
        session.add(test_article_order)
        session.commit()
        session.refresh(test_article_order)
        article_order_id = test_article_order.id

    # Make request
    response = client.get(f"/article-orders/{article_order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["article_req_id"] == article_id
    assert data["status_id"] == article_order_status_id
    assert data["position"] == 1
    assert data["quantity"] == "10.5"
    assert data["unit"] == "pcs"
    assert data["brand"] == "Test Brand"
    assert data["model"] == "Test Model"
    assert data["unit_price"] == "100.00"
    assert data["total"] == "1050.00"
    assert data["notes"] == "Test notes"

    # Clean up
    with Session(engine) as session:
        session.delete(test_article_order)
        session.commit()
    cleanup_test_dependencies(
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_create_article_order():
    # Create dependencies
    (
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Data for the new article order
    new_article_order_data = {
        "order_id": order_id,
        "article_req_id": article_id,
        "status_id": article_order_status_id,
        "position": 1,
        "quantity": "10.5",
        "unit": "pcs",
        "brand": "Test Brand",
        "model": "Test Model",
        "unit_price": "100.00",
        "total": "1050.00",
        "notes": "Test notes"
    }

    # Make request
    response = client.post("/article-orders/", json=new_article_order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["article_req_id"] == article_id
    assert data["status_id"] == article_order_status_id
    assert data["position"] == 1
    assert data["quantity"] == "10.5"
    assert data["unit"] == "pcs"
    assert data["brand"] == "Test Brand"
    assert data["model"] == "Test Model"
    assert data["unit_price"] == "100.00"
    assert data["total"] == "1050.00"
    assert data["notes"] == "Test notes"

    # Clean up
    with Session(engine) as session:
        statement = select(ArticleOrder).where(
            ArticleOrder.order_id == order_id,
            ArticleOrder.article_req_id == article_id
        )
        test_article_order = session.exec(statement).first()
        if test_article_order:
            session.delete(test_article_order)
            session.commit()
    cleanup_test_dependencies(
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_create_article_order_invalid_references():
    # Create dependencies
    (
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Data with invalid references
    invalid_data = {
        "order_id": 99999,  # Invalid order ID
        "article_req_id": article_id,
        "status_id": article_order_status_id,
        "position": 1,
        "quantity": "10.5",
        "unit": "pcs",
        "brand": "Test Brand",
        "model": "Test Model",
        "unit_price": "100.00",
        "total": "1050.00",
        "notes": "Test notes"
    }

    # Make request
    response = client.post("/article-orders/", json=invalid_data)
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]

    # Clean up dependencies
    cleanup_test_dependencies(
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_delete_article_order():
    # Create dependencies
    (
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    ) = create_test_dependencies()

    # Create test article order
    test_article_order = ArticleOrder(
        order_id=order_id,
        article_req_id=article_id,
        status_id=article_order_status_id,
        position=1,
        quantity=Decimal("10.5"),
        unit="pcs",
        brand="Test Brand",
        model="Test Model",
        unit_price=Decimal("100.00"),
        total=Decimal("1050.00"),
        notes="Test notes"
    )
    with Session(engine) as session:
        session.add(test_article_order)
        session.commit()
        session.refresh(test_article_order)
        article_order_id = test_article_order.id

    # Make request
    response = client.delete(f"/article-orders/{article_order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Article order deleted"

    # Verify deletion
    with Session(engine) as session:
        statement = select(ArticleOrder).where(ArticleOrder.id == article_order_id)
        deleted_article_order = session.exec(statement).first()
        assert deleted_article_order is None

    # Clean up dependencies
    cleanup_test_dependencies(
        order_id, article_id, article_order_status_id,
        supplier_id, payment_condition_id, address_id,
        order_status_id, user1_id, user2_id, user3_id, user4_id
    )

def test_delete_nonexistent_article_order():
    response = client.delete("/article-orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article order not found"

def test_delete_article_order_not_found():
    """Test deleting a non-existent article order"""
    response = client.delete("/article-orders/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article order not found"

def test_update_article_order():
    """Test updating an article order"""
    # Create dependencies
    with Session(engine) as session:
        # Create address
        address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="México"
        )
        session.add(address)
        session.commit()
        address_id = address.id

        # Create payment condition
        payment_condition = PaymentCondition(
            name="Test Payment Condition Update",
            description="Test Description",
            text="Test Text",
            active=True
        )
        session.add(payment_condition)
        session.commit()
        payment_condition_id = payment_condition.id

        # Create supplier
        supplier = Supplier(
            name="Test Supplier Update",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="30 days",
            payment_condition_id=payment_condition_id,
            currency="USD"
        )
        session.add(supplier)
        session.commit()
        supplier_id = supplier.id

        # Create order status
        order_status = OrderStatus(
            name="Test Order Status Update",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(order_status)
        session.commit()
        order_status_id = order_status.id

        # Create article order status
        article_order_status = ArticleOrderStatus(
            name="Test Article Order Status Update",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(article_order_status)
        session.commit()
        article_order_status_id = article_order_status.id

        # Create article state
        article_state = ArticleState(
            name="Test Article State Update",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(article_state)
        session.commit()
        article_state_id = article_state.id

        # Create users
        user1 = User(
            username="testuser1_update",
            full_name="Test User 1",
            password_hash="hashedpassword1"
        )
        user2 = User(
            username="testuser2_update",
            full_name="Test User 2",
            password_hash="hashedpassword2"
        )
        user3 = User(
            username="testuser3_update",
            full_name="Test User 3",
            password_hash="hashedpassword3"
        )
        user4 = User(
            username="testuser4_update",
            full_name="Test User 4",
            password_hash="hashedpassword4"
        )
        session.add_all([user1, user2, user3, user4])
        session.commit()
        user1_id = user1.id
        user2_id = user2.id
        user3_id = user3.id
        user4_id = user4.id

        # Create order
        order = Order(
            supplier_id=supplier_id,
            address="Test Address",
            bank_details="Test Bank Details",
            date=datetime.utcnow(),
            delivery_time=datetime.utcnow(),
            payment_condition_id=payment_condition_id,
            currency="EUR",
            supplier_reference="TEST123",
            acceptance_id=user1_id,
            requested_by_id=user2_id,
            reviewed_by_id=user3_id,
            approved_by_id=user4_id,
            subtotal=Decimal("100.00"),
            vat=Decimal("21.00"),
            discount=Decimal("0.00"),
            total=Decimal("121.00"),
            notes="Test Notes",
            shipping_address_id=address_id,
            status_id=order_status_id
        )
        session.add(order)
        session.commit()
        order_id = order.id

        # Create article
        article = Article(
            name="Test Article",
            description="Test Description",
            quantity=Decimal("10.00"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x20x30",
            state_id=article_state_id,
            active=True
        )
        session.add(article)
        session.commit()
        article_id = article.id

        # Create initial article order
        article_order = ArticleOrder(
            order_id=order_id,
            article_req_id=article_id,
            status_id=article_order_status_id,
            position=1,
            quantity=Decimal("10.00"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            unit_price=Decimal("10.00"),
            total=Decimal("100.00"),
            notes="Test Notes"
        )
        session.add(article_order)
        session.commit()
        article_order_id = article_order.id

    # Update the article order
    update_data = {
        "position": 2,
        "quantity": "20.00",
        "unit": "kg",
        "brand": "Updated Brand",
        "model": "Updated Model",
        "unit_price": "15.00",
        "total": "300.00",
        "notes": "Updated Notes"
    }
    response = client.put(f"/article-orders/{article_order_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_order_id
    assert data["position"] == 2
    assert data["quantity"] == "20.00"
    assert data["unit"] == "kg"
    assert data["brand"] == "Updated Brand"
    assert data["model"] == "Updated Model"
    assert data["unit_price"] == "15.00"
    assert data["total"] == "300.00"
    assert data["notes"] == "Updated Notes"

    # Verify database state
    with Session(engine) as session:
        updated_article_order = session.get(ArticleOrder, article_order_id)
        assert updated_article_order.position == 2
        assert updated_article_order.quantity == Decimal("20.00")
        assert updated_article_order.unit == "kg"
        assert updated_article_order.brand == "Updated Brand"
        assert updated_article_order.model == "Updated Model"
        assert updated_article_order.unit_price == Decimal("15.00")
        assert updated_article_order.total == Decimal("300.00")
        assert updated_article_order.notes == "Updated Notes"

        # Cleanup
        session.delete(updated_article_order)
        session.delete(order)
        session.delete(article)
        session.delete(article_state)
        session.delete(article_order_status)
        session.delete(order_status)
        session.delete(supplier)
        session.delete(payment_condition)
        session.delete(address)
        session.delete(user1)
        session.delete(user2)
        session.delete(user3)
        session.delete(user4)
        session.commit()

def test_update_article_order_not_found():
    """Test updating a non-existent article order"""
    update_data = {
        "position": 2,
        "quantity": "20.00"
    }
    response = client.put("/article-orders/999999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Article order not found"

def test_update_article_order_invalid_order():
    """Test updating an article order with an invalid order ID"""
    # Create dependencies
    with Session(engine) as session:
        # Create address
        address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="México"
        )
        session.add(address)
        session.commit()
        address_id = address.id

        # Create payment condition
        payment_condition = PaymentCondition(
            name="Test Payment Condition Invalid",
            description="Test Description",
            text="Test Text",
            active=True
        )
        session.add(payment_condition)
        session.commit()
        payment_condition_id = payment_condition.id

        # Create supplier
        supplier = Supplier(
            name="Test Supplier Invalid",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="30 days",
            payment_condition_id=payment_condition_id,
            currency="USD"
        )
        session.add(supplier)
        session.commit()
        supplier_id = supplier.id

        # Create order status
        order_status = OrderStatus(
            name="Test Order Status Invalid",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(order_status)
        session.commit()
        order_status_id = order_status.id

        # Create article order status
        article_order_status = ArticleOrderStatus(
            name="Test Article Order Status Invalid",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(article_order_status)
        session.commit()
        article_order_status_id = article_order_status.id

        # Create article state
        article_state = ArticleState(
            name="Test Article State Invalid",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(article_state)
        session.commit()
        article_state_id = article_state.id

        # Create users
        user1 = User(
            username="testuser1_invalid",
            full_name="Test User 1",
            password_hash="hashedpassword1"
        )
        user2 = User(
            username="testuser2_invalid",
            full_name="Test User 2",
            password_hash="hashedpassword2"
        )
        user3 = User(
            username="testuser3_invalid",
            full_name="Test User 3",
            password_hash="hashedpassword3"
        )
        user4 = User(
            username="testuser4_invalid",
            full_name="Test User 4",
            password_hash="hashedpassword4"
        )
        session.add_all([user1, user2, user3, user4])
        session.commit()
        user1_id = user1.id
        user2_id = user2.id
        user3_id = user3.id
        user4_id = user4.id

        # Create order
        order = Order(
            supplier_id=supplier_id,
            address="Test Address",
            bank_details="Test Bank Details",
            date=datetime.utcnow(),
            delivery_time=datetime.utcnow(),
            payment_condition_id=payment_condition_id,
            currency="EUR",
            supplier_reference="TEST123",
            acceptance_id=user1_id,
            requested_by_id=user2_id,
            reviewed_by_id=user3_id,
            approved_by_id=user4_id,
            subtotal=Decimal("100.00"),
            vat=Decimal("21.00"),
            discount=Decimal("0.00"),
            total=Decimal("121.00"),
            notes="Test Notes",
            shipping_address_id=address_id,
            status_id=order_status_id
        )
        session.add(order)
        session.commit()
        order_id = order.id

        # Create article
        article = Article(
            name="Test Article",
            description="Test Description",
            quantity=Decimal("10.00"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x20x30",
            state_id=article_state_id,
            active=True
        )
        session.add(article)
        session.commit()
        article_id = article.id

        # Create initial article order
        article_order = ArticleOrder(
            order_id=order_id,
            article_req_id=article_id,
            status_id=article_order_status_id,
            position=1,
            quantity=Decimal("10.00"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            unit_price=Decimal("10.00"),
            total=Decimal("100.00"),
            notes="Test Notes"
        )
        session.add(article_order)
        session.commit()
        article_order_id = article_order.id

    # Try to update with invalid order ID
    update_data = {
        "order_id": 999999
    }
    response = client.put(f"/article-orders/{article_order_id}", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

    # Cleanup
    with Session(engine) as session:
        session.delete(article_order)
        session.delete(order)
        session.delete(article)
        session.delete(article_state)
        session.delete(article_order_status)
        session.delete(order_status)
        session.delete(supplier)
        session.delete(payment_condition)
        session.delete(address)
        session.delete(user1)
        session.delete(user2)
        session.delete(user3)
        session.delete(user4)
        session.commit()

def test_update_article_order_partial():
    """Test partial update of an article order"""
    # Create dependencies
    with Session(engine) as session:
        # Create address
        address = Address(
            street="Test Street",
            exterior_number="123",
            neighborhood="Test Neighborhood",
            postal_code="12345",
            city="Test City",
            state="Test State",
            country="México"
        )
        session.add(address)
        session.commit()
        address_id = address.id

        # Create payment condition
        payment_condition = PaymentCondition(
            name="Test Payment Condition Partial",
            description="Test Description",
            text="Test Text",
            active=True
        )
        session.add(payment_condition)
        session.commit()
        payment_condition_id = payment_condition.id

        # Create supplier
        supplier = Supplier(
            name="Test Supplier Partial",
            rfc="TEST123456789",
            address_id=address_id,
            bank_details="Test Bank Details",
            delivery_time="30 days",
            payment_condition_id=payment_condition_id,
            currency="USD"
        )
        session.add(supplier)
        session.commit()
        supplier_id = supplier.id

        # Create order status
        order_status = OrderStatus(
            name="Test Order Status Partial",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(order_status)
        session.commit()
        order_status_id = order_status.id

        # Create article order status
        article_order_status = ArticleOrderStatus(
            name="Test Article Order Status Partial",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(article_order_status)
        session.commit()
        article_order_status_id = article_order_status.id

        # Create article state
        article_state = ArticleState(
            name="Test Article State Partial",
            description="Test Description",
            order=1,
            active=True
        )
        session.add(article_state)
        session.commit()
        article_state_id = article_state.id

        # Create users
        user1 = User(
            username="testuser1_partial",
            full_name="Test User 1",
            password_hash="hashedpassword1"
        )
        user2 = User(
            username="testuser2_partial",
            full_name="Test User 2",
            password_hash="hashedpassword2"
        )
        user3 = User(
            username="testuser3_partial",
            full_name="Test User 3",
            password_hash="hashedpassword3"
        )
        user4 = User(
            username="testuser4_partial",
            full_name="Test User 4",
            password_hash="hashedpassword4"
        )
        session.add_all([user1, user2, user3, user4])
        session.commit()
        user1_id = user1.id
        user2_id = user2.id
        user3_id = user3.id
        user4_id = user4.id

        # Create order
        order = Order(
            supplier_id=supplier_id,
            address="Test Address",
            bank_details="Test Bank Details",
            date=datetime.utcnow(),
            delivery_time=datetime.utcnow(),
            payment_condition_id=payment_condition_id,
            currency="EUR",
            supplier_reference="TEST123",
            acceptance_id=user1_id,
            requested_by_id=user2_id,
            reviewed_by_id=user3_id,
            approved_by_id=user4_id,
            subtotal=Decimal("100.00"),
            vat=Decimal("21.00"),
            discount=Decimal("0.00"),
            total=Decimal("121.00"),
            notes="Test Notes",
            shipping_address_id=address_id,
            status_id=order_status_id
        )
        session.add(order)
        session.commit()
        order_id = order.id

        # Create article
        article = Article(
            name="Test Article",
            description="Test Description",
            quantity=Decimal("10.00"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            dimensions="10x20x30",
            state_id=article_state_id,
            active=True
        )
        session.add(article)
        session.commit()
        article_id = article.id

        # Create initial article order
        article_order = ArticleOrder(
            order_id=order_id,
            article_req_id=article_id,
            status_id=article_order_status_id,
            position=1,
            quantity=Decimal("10.00"),
            unit="pcs",
            brand="Test Brand",
            model="Test Model",
            unit_price=Decimal("10.00"),
            total=Decimal("100.00"),
            notes="Test Notes"
        )
        session.add(article_order)
        session.commit()
        article_order_id = article_order.id

    # Update only position and notes
    update_data = {
        "position": 2,
        "notes": "Updated Notes"
    }
    response = client.put(f"/article-orders/{article_order_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_order_id
    assert data["position"] == 2
    assert data["notes"] == "Updated Notes"
    # Verify other fields remain unchanged
    assert data["quantity"] == "10.00"
    assert data["unit"] == "pcs"
    assert data["brand"] == "Test Brand"
    assert data["model"] == "Test Model"
    assert data["unit_price"] == "10.00"
    assert data["total"] == "100.00"

    # Cleanup
    with Session(engine) as session:
        session.delete(article_order)
        session.delete(order)
        session.delete(article)
        session.delete(article_state)
        session.delete(article_order_status)
        session.delete(order_status)
        session.delete(supplier)
        session.delete(payment_condition)
        session.delete(address)
        session.delete(user1)
        session.delete(user2)
        session.delete(user3)
        session.delete(user4)
        session.commit() 
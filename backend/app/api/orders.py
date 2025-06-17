from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import (
    Order, OrderCreate, OrderResponse, OrderUpdate, Supplier, PaymentCondition, 
    Address, OrderStatus, User, OrderWithArticlesCreate,
    ArticleOrder, Article, ArticleOrderStatus
)
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=list[OrderResponse])
def get_orders(session: Session = Depends(get_session)):
    """Get all orders"""
    statement = select(Order)
    results = session.exec(statement)
    return [{
        "id": order.id,
        "supplier_id": order.supplier_id,
        "address": order.address,
        "bank_details": order.bank_details,
        "date": order.date,
        "delivery_time": order.delivery_time,
        "payment_condition_id": order.payment_condition_id,
        "currency": order.currency,
        "supplier_reference": order.supplier_reference,
        "acceptance_id": order.acceptance_id,
        "requested_by_id": order.requested_by_id,
        "reviewed_by_id": order.reviewed_by_id,
        "approved_by_id": order.approved_by_id,
        "subtotal": order.subtotal,
        "vat": order.vat,
        "discount": order.discount,
        "total": order.total,
        "notes": order.notes,
        "shipping_address_id": order.shipping_address_id,
        "status_id": order.status_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    } for order in results]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, session: Session = Depends(get_session)):
    """Get a specific order by ID"""
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "supplier_id": order.supplier_id,
        "address": order.address,
        "bank_details": order.bank_details,
        "date": order.date,
        "delivery_time": order.delivery_time,
        "payment_condition_id": order.payment_condition_id,
        "currency": order.currency,
        "supplier_reference": order.supplier_reference,
        "acceptance_id": order.acceptance_id,
        "requested_by_id": order.requested_by_id,
        "reviewed_by_id": order.reviewed_by_id,
        "approved_by_id": order.approved_by_id,
        "subtotal": order.subtotal,
        "vat": order.vat,
        "discount": order.discount,
        "total": order.total,
        "notes": order.notes,
        "shipping_address_id": order.shipping_address_id,
        "status_id": order.status_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    """Create a new order"""
    # Verify that the supplier exists
    supplier = session.get(Supplier, order.supplier_id)
    if not supplier:
        raise HTTPException(status_code=400, detail="Supplier not found")

    # Verify that the payment condition exists
    payment_condition = session.get(PaymentCondition, order.payment_condition_id)
    if not payment_condition:
        raise HTTPException(status_code=400, detail="Payment condition not found")

    # Verify that the shipping address exists
    shipping_address = session.get(Address, order.shipping_address_id)
    if not shipping_address:
        raise HTTPException(status_code=400, detail="Shipping address not found")

    # Verify that the status exists
    status = session.get(OrderStatus, order.status_id)
    if not status:
        raise HTTPException(status_code=400, detail="Order status not found")

    # Verify that the users exist if provided
    if order.acceptance_id:
        user = session.get(User, order.acceptance_id)
        if not user:
            raise HTTPException(status_code=400, detail="Acceptance user not found")
    
    if order.requested_by_id:
        user = session.get(User, order.requested_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Requested by user not found")
    
    if order.reviewed_by_id:
        user = session.get(User, order.reviewed_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Reviewed by user not found")
    
    if order.approved_by_id:
        user = session.get(User, order.approved_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Approved by user not found")

    db_order = Order.model_validate(order)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return {
        "id": db_order.id,
        "supplier_id": db_order.supplier_id,
        "address": db_order.address,
        "bank_details": db_order.bank_details,
        "date": db_order.date,
        "delivery_time": db_order.delivery_time,
        "payment_condition_id": db_order.payment_condition_id,
        "currency": db_order.currency,
        "supplier_reference": db_order.supplier_reference,
        "acceptance_id": db_order.acceptance_id,
        "requested_by_id": db_order.requested_by_id,
        "reviewed_by_id": db_order.reviewed_by_id,
        "approved_by_id": db_order.approved_by_id,
        "subtotal": db_order.subtotal,
        "vat": db_order.vat,
        "discount": db_order.discount,
        "total": db_order.total,
        "notes": db_order.notes,
        "shipping_address_id": db_order.shipping_address_id,
        "status_id": db_order.status_id,
        "created_at": db_order.created_at,
        "updated_at": db_order.updated_at
    }

@router.post("/with-articles", response_model=OrderResponse)
def create_order_with_articles(
    data: OrderWithArticlesCreate,
    session: Session = Depends(get_session)
):
    """Create an order with its associated article orders"""
    # Verify that the referenced entities exist for the order
    if data.order.supplier_id:
        supplier = session.get(Supplier, data.order.supplier_id)
        if not supplier:
            raise HTTPException(status_code=400, detail="Invalid supplier_id")
    
    if data.order.payment_condition_id:
        payment_condition = session.get(PaymentCondition, data.order.payment_condition_id)
        if not payment_condition:
            raise HTTPException(status_code=400, detail="Invalid payment_condition_id")
    
    if data.order.shipping_address_id:
        shipping_address = session.get(Address, data.order.shipping_address_id)
        if not shipping_address:
            raise HTTPException(status_code=400, detail="Invalid shipping_address_id")
    
    if data.order.status_id:
        status = session.get(OrderStatus, data.order.status_id)
        if not status:
            raise HTTPException(status_code=400, detail="Invalid status_id")

    # Verify that the users exist if provided
    if data.order.acceptance_id:
        user = session.get(User, data.order.acceptance_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid acceptance_id")
    
    if data.order.requested_by_id:
        user = session.get(User, data.order.requested_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid requested_by_id")
    
    if data.order.reviewed_by_id:
        user = session.get(User, data.order.reviewed_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid reviewed_by_id")
    
    if data.order.approved_by_id:
        user = session.get(User, data.order.approved_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid approved_by_id")

    # Create the order
    db_order = Order.model_validate(data.order)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    # Create the article orders
    created_article_orders = []
    for article_data in data.articles:
        # Verify that the referenced entities exist for each article order
        if article_data.article_req_id:
            article = session.get(Article, article_data.article_req_id)
            if not article:
                raise HTTPException(status_code=400, detail="Invalid article_req_id")
        
        if article_data.status_id:
            article_order_status = session.get(ArticleOrderStatus, article_data.status_id)
            if not article_order_status:
                raise HTTPException(status_code=400, detail="Invalid article order status_id")
        
        # Create the article order with the order_id
        db_article_order = ArticleOrder(
            order_id=db_order.id,
            article_req_id=article_data.article_req_id,
            status_id=article_data.status_id,
            position=article_data.position,
            quantity=article_data.quantity,
            unit=article_data.unit,
            brand=article_data.brand,
            model=article_data.model,
            unit_price=article_data.unit_price,
            total=article_data.total,
            notes=article_data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(db_article_order)
        created_article_orders.append(db_article_order)
    
    session.commit()
    session.refresh(db_order)
    
    return {
        "id": db_order.id,
        "supplier_id": db_order.supplier_id,
        "address": db_order.address,
        "bank_details": db_order.bank_details,
        "date": db_order.date,
        "delivery_time": db_order.delivery_time,
        "payment_condition_id": db_order.payment_condition_id,
        "currency": db_order.currency,
        "supplier_reference": db_order.supplier_reference,
        "acceptance_id": db_order.acceptance_id,
        "requested_by_id": db_order.requested_by_id,
        "reviewed_by_id": db_order.reviewed_by_id,
        "approved_by_id": db_order.approved_by_id,
        "subtotal": db_order.subtotal,
        "vat": db_order.vat,
        "discount": db_order.discount,
        "total": db_order.total,
        "notes": db_order.notes,
        "shipping_address_id": db_order.shipping_address_id,
        "status_id": db_order.status_id,
        "created_at": db_order.created_at,
        "updated_at": db_order.updated_at
    }

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, session: Session = Depends(get_session)):
    """Update an existing order"""
    # Get the existing order
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify that the supplier exists if being updated
    if order_update.supplier_id is not None:
        supplier = session.get(Supplier, order_update.supplier_id)
        if not supplier:
            raise HTTPException(status_code=400, detail="Supplier not found")

    # Verify that the payment condition exists if being updated
    if order_update.payment_condition_id is not None:
        payment_condition = session.get(PaymentCondition, order_update.payment_condition_id)
        if not payment_condition:
            raise HTTPException(status_code=400, detail="Payment condition not found")

    # Verify that the shipping address exists if being updated
    if order_update.shipping_address_id is not None:
        shipping_address = session.get(Address, order_update.shipping_address_id)
        if not shipping_address:
            raise HTTPException(status_code=400, detail="Shipping address not found")

    # Verify that the status exists if being updated
    if order_update.status_id is not None:
        status = session.get(OrderStatus, order_update.status_id)
        if not status:
            raise HTTPException(status_code=400, detail="Order status not found")

    # Verify that the users exist if being updated
    if order_update.acceptance_id is not None:
        user = session.get(User, order_update.acceptance_id)
        if not user:
            raise HTTPException(status_code=400, detail="Acceptance user not found")
    
    if order_update.requested_by_id is not None:
        user = session.get(User, order_update.requested_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Requested by user not found")
    
    if order_update.reviewed_by_id is not None:
        user = session.get(User, order_update.reviewed_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Reviewed by user not found")
    
    if order_update.approved_by_id is not None:
        user = session.get(User, order_update.approved_by_id)
        if not user:
            raise HTTPException(status_code=400, detail="Approved by user not found")

    # Update only the fields that were provided
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Update the updated_at timestamp
    order.updated_at = datetime.utcnow()

    session.add(order)
    session.commit()
    session.refresh(order)

    return {
        "id": order.id,
        "supplier_id": order.supplier_id,
        "address": order.address,
        "bank_details": order.bank_details,
        "date": order.date,
        "delivery_time": order.delivery_time,
        "payment_condition_id": order.payment_condition_id,
        "currency": order.currency,
        "supplier_reference": order.supplier_reference,
        "acceptance_id": order.acceptance_id,
        "requested_by_id": order.requested_by_id,
        "reviewed_by_id": order.reviewed_by_id,
        "approved_by_id": order.approved_by_id,
        "subtotal": order.subtotal,
        "vat": order.vat,
        "discount": order.discount,
        "total": order.total,
        "notes": order.notes,
        "shipping_address_id": order.shipping_address_id,
        "status_id": order.status_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }

@router.delete("/{order_id}")
def delete_order(order_id: int, session: Session = Depends(get_session)):
    """Delete an order"""
    # First check if the order exists
    statement = select(Order).where(Order.id == order_id)
    order = session.exec(statement).one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if the order has any articles
    # if order.articles:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Cannot delete order that has articles"
    #     )
    
    statement = delete(Order).where(Order.id == order_id)
    session.exec(statement)
    session.commit()
    return {"message": "Order deleted"} 
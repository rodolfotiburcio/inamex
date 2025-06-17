from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import (
    ArticleOrder, ArticleOrderCreate, ArticleOrderResponse, ArticleOrderUpdate,
    Order, Article, ArticleOrderStatus
)
from decimal import Decimal
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ArticleOrderResponse])
def get_article_orders(session: Session = Depends(get_session)):
    """Get all article orders"""
    statement = select(ArticleOrder)
    results = session.exec(statement)
    return [{
        "id": article_order.id,
        "order_id": article_order.order_id,
        "article_req_id": article_order.article_req_id,
        "status_id": article_order.status_id,
        "position": article_order.position,
        "quantity": article_order.quantity,
        "unit": article_order.unit,
        "brand": article_order.brand,
        "model": article_order.model,
        "unit_price": article_order.unit_price,
        "total": article_order.total,
        "notes": article_order.notes,
        "created_at": article_order.created_at,
        "updated_at": article_order.updated_at
    } for article_order in results]

@router.get("/{article_order_id}", response_model=ArticleOrderResponse)
def get_article_order(article_order_id: int, session: Session = Depends(get_session)):
    """Get a specific article order by ID"""
    statement = select(ArticleOrder).where(ArticleOrder.id == article_order_id)
    result = session.exec(statement)
    article_order = result.one_or_none()
    if not article_order:
        raise HTTPException(status_code=404, detail="Article order not found")
    return {
        "id": article_order.id,
        "order_id": article_order.order_id,
        "article_req_id": article_order.article_req_id,
        "status_id": article_order.status_id,
        "position": article_order.position,
        "quantity": article_order.quantity,
        "unit": article_order.unit,
        "brand": article_order.brand,
        "model": article_order.model,
        "unit_price": article_order.unit_price,
        "total": article_order.total,
        "notes": article_order.notes,
        "created_at": article_order.created_at,
        "updated_at": article_order.updated_at
    }

@router.post("/", response_model=ArticleOrderResponse)
def create_article_order(article_order: ArticleOrderCreate, session: Session = Depends(get_session)):
    """Create a new article order"""
    # Verify that the order exists
    order = session.exec(select(Order).where(Order.id == article_order.order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify that the article exists if provided
    if article_order.article_req_id:
        article = session.exec(select(Article).where(Article.id == article_order.article_req_id)).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

    # Verify that the status exists
    status = session.exec(select(ArticleOrderStatus).where(ArticleOrderStatus.id == article_order.status_id)).first()
    if not status:
        raise HTTPException(status_code=404, detail="Article order status not found")

    db_article_order = ArticleOrder.model_validate(article_order)
    session.add(db_article_order)
    session.commit()
    session.refresh(db_article_order)
    return {
        "id": db_article_order.id,
        "order_id": db_article_order.order_id,
        "article_req_id": db_article_order.article_req_id,
        "status_id": db_article_order.status_id,
        "position": db_article_order.position,
        "quantity": db_article_order.quantity,
        "unit": db_article_order.unit,
        "brand": db_article_order.brand,
        "model": db_article_order.model,
        "unit_price": db_article_order.unit_price,
        "total": db_article_order.total,
        "notes": db_article_order.notes,
        "created_at": db_article_order.created_at,
        "updated_at": db_article_order.updated_at
    }

@router.delete("/{article_order_id}", response_model=dict)
def delete_article_order(article_order_id: int, session: Session = Depends(get_session)):
    """Delete an article order by ID"""
    statement = select(ArticleOrder).where(ArticleOrder.id == article_order_id)
    article_order = session.exec(statement).first()
    
    if not article_order:
        raise HTTPException(status_code=404, detail="Article order not found")
    
    session.delete(article_order)
    session.commit()
    
    return {"message": "Article order deleted"}

@router.put("/{article_order_id}", response_model=ArticleOrderResponse)
def update_article_order(article_order_id: int, article_order_update: ArticleOrderUpdate, session: Session = Depends(get_session)):
    """Update an article order by ID"""
    # Get the existing article order
    statement = select(ArticleOrder).where(ArticleOrder.id == article_order_id)
    result = session.exec(statement)
    article_order = result.one_or_none()
    if not article_order:
        raise HTTPException(status_code=404, detail="Article order not found")

    # Verify that the order exists if being updated
    if article_order_update.order_id is not None:
        order = session.exec(select(Order).where(Order.id == article_order_update.order_id)).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

    # Verify that the article exists if being updated
    if article_order_update.article_req_id is not None:
        article = session.exec(select(Article).where(Article.id == article_order_update.article_req_id)).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

    # Verify that the status exists if being updated
    if article_order_update.status_id is not None:
        status = session.exec(select(ArticleOrderStatus).where(ArticleOrderStatus.id == article_order_update.status_id)).first()
        if not status:
            raise HTTPException(status_code=404, detail="Article order status not found")

    # Update the article order with the provided fields
    article_order_data = article_order_update.model_dump(exclude_unset=True)
    for key, value in article_order_data.items():
        if key in ["quantity", "unit_price", "total"] and value is not None:
            setattr(article_order, key, Decimal(str(value)))
        else:
            setattr(article_order, key, value)

    # Update the updated_at timestamp
    article_order.updated_at = datetime.utcnow()

    session.add(article_order)
    session.commit()
    session.refresh(article_order)

    return {
        "id": article_order.id,
        "order_id": article_order.order_id,
        "article_req_id": article_order.article_req_id,
        "status_id": article_order.status_id,
        "position": article_order.position,
        "quantity": article_order.quantity,
        "unit": article_order.unit,
        "brand": article_order.brand,
        "model": article_order.model,
        "unit_price": article_order.unit_price,
        "total": article_order.total,
        "notes": article_order.notes,
        "created_at": article_order.created_at,
        "updated_at": article_order.updated_at
    } 
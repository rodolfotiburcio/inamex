from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import ArticleOrderStatus, ArticleOrderStatusCreate, ArticleOrderStatusResponse, ArticleOrderStatusUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ArticleOrderStatusResponse])
def get_article_order_statuses(session: Session = Depends(get_session)):
    """Get all article order statuses"""
    statement = select(ArticleOrderStatus)
    results = session.exec(statement)
    return [{
        "id": status.id,
        "name": status.name,
        "description": status.description,
        "order": status.order,
        "active": status.active,
        "created_at": status.created_at,
        "updated_at": status.updated_at
    } for status in results]

@router.get("/{status_id}", response_model=ArticleOrderStatusResponse)
def get_article_order_status(status_id: int, session: Session = Depends(get_session)):
    """Get a specific article order status by ID"""
    statement = select(ArticleOrderStatus).where(ArticleOrderStatus.id == status_id)
    result = session.exec(statement)
    status = result.one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Article order status not found")
    return {
        "id": status.id,
        "name": status.name,
        "description": status.description,
        "order": status.order,
        "active": status.active,
        "created_at": status.created_at,
        "updated_at": status.updated_at
    }

@router.post("/", response_model=ArticleOrderStatusResponse)
def create_article_order_status(status: ArticleOrderStatusCreate, session: Session = Depends(get_session)):
    """Create a new article order status"""
    # Verificar si ya existe un estado con ese nombre
    existing_status = session.exec(
        select(ArticleOrderStatus).where(ArticleOrderStatus.name == status.name)
    ).one_or_none()
    
    if existing_status:
        raise HTTPException(
            status_code=409,
            detail=f"Article order status with name '{status.name}' already exists"
        )
    
    # Si no existe, proceder con la creación
    
    db_status = ArticleOrderStatus.model_validate(status)
    session.add(db_status)
    session.commit()
    session.refresh(db_status)
    return {
        "id": db_status.id,
        "name": db_status.name,
        "description": db_status.description,
        "order": db_status.order,
        "active": db_status.active,
        "created_at": db_status.created_at,
        "updated_at": db_status.updated_at
    }

@router.delete("/{status_id}")
def delete_article_order_status(status_id: int, session: Session = Depends(get_session)):
    """Delete an article order status"""
    # First check if the status is being used by any article order
    statement = select(ArticleOrderStatus).where(ArticleOrderStatus.id == status_id)
    status = session.exec(statement).one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Article order status not found")
    
    # Check if the status has any articles
    if status.articles:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete status that is being used by article orders"
        )
    
    statement = delete(ArticleOrderStatus).where(ArticleOrderStatus.id == status_id)
    session.exec(statement)
    session.commit()
    return {"message": "Article order status deleted"}

@router.put("/{status_id}", response_model=ArticleOrderStatusResponse)
def update_article_order_status(status_id: int, status_update: ArticleOrderStatusUpdate, session: Session = Depends(get_session)):
    """Update an article order status"""
    # Get the existing status
    statement = select(ArticleOrderStatus).where(ArticleOrderStatus.id == status_id)
    result = session.exec(statement)
    status = result.one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Article order status not found")
    
    # If name is being updated, check if it conflicts with existing status
    if status_update.name is not None and status_update.name != status.name:
        existing_status = session.exec(
            select(ArticleOrderStatus).where(ArticleOrderStatus.name == status_update.name)
        ).one_or_none()
        if existing_status:
            raise HTTPException(
                status_code=409,
                detail=f"Article order status with name '{status_update.name}' already exists"
            )
    
    # Update the status with the provided fields
    status_data = status_update.model_dump(exclude_unset=True)
    for key, value in status_data.items():
        setattr(status, key, value)
    
    # Update the updated_at timestamp
    status.updated_at = datetime.utcnow()
    
    session.add(status)
    session.commit()
    session.refresh(status)
    
    return {
        "id": status.id,
        "name": status.name,
        "description": status.description,
        "order": status.order,
        "active": status.active,
        "created_at": status.created_at,
        "updated_at": status.updated_at
    } 
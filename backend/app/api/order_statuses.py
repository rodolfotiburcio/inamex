from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import OrderStatus, OrderStatusCreate, OrderStatusResponse, OrderStatusUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[OrderStatusResponse])
def get_order_statuses(session: Session = Depends(get_session)):
    statement = select(OrderStatus)
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

@router.get("/{status_id}", response_model=OrderStatusResponse)
def get_order_status(status_id: int, session: Session = Depends(get_session)):
    statement = select(OrderStatus).where(OrderStatus.id == status_id)
    result = session.exec(statement)
    status = result.one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Order status not found")
    return {
        "id": status.id,
        "name": status.name,
        "description": status.description,
        "order": status.order,
        "active": status.active,
        "created_at": status.created_at,
        "updated_at": status.updated_at
    }
    
@router.delete("/{status_id}")
def delete_order_status(status_id: int, session: Session = Depends(get_session)):
    statement = delete(OrderStatus).where(OrderStatus.id == status_id)
    session.exec(statement)
    session.commit()
    return {"message": "Order status deleted"}

@router.post("/", response_model=OrderStatusResponse)
def create_order_status(status: OrderStatusCreate, session: Session = Depends(get_session)):
    db_status = OrderStatus.model_validate(status)
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

@router.put("/{status_id}", response_model=OrderStatusResponse)
def update_order_status(status_id: int, status_update: OrderStatusUpdate, session: Session = Depends(get_session)):
    # Get the existing status
    statement = select(OrderStatus).where(OrderStatus.id == status_id)
    result = session.exec(statement)
    status = result.one_or_none()
    if not status:
        raise HTTPException(status_code=404, detail="Order status not found")
    
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
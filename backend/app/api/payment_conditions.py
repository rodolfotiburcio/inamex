from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models import PaymentCondition, PaymentConditionCreate, PaymentConditionResponse, PaymentConditionUpdate
from app.core.database import get_session
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[PaymentConditionResponse])
def get_payment_conditions(session: Session = Depends(get_session)):
    """Get all payment conditions"""
    statement = select(PaymentCondition)
    conditions = session.exec(statement).all()
    return conditions

@router.get("/{condition_id}", response_model=PaymentConditionResponse)
def get_payment_condition(condition_id: int, session: Session = Depends(get_session)):
    """Get a specific payment condition by ID"""
    condition = session.get(PaymentCondition, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Payment condition not found")
    return condition

@router.post("/", response_model=PaymentConditionResponse)
def create_payment_condition(condition: PaymentConditionCreate, session: Session = Depends(get_session)):
    """Create a new payment condition"""
    db_condition = PaymentCondition.model_validate(condition)
    session.add(db_condition)
    session.commit()
    session.refresh(db_condition)
    return db_condition

@router.delete("/{condition_id}")
def delete_payment_condition(condition_id: int, session: Session = Depends(get_session)):
    """Delete a payment condition"""
    condition = session.get(PaymentCondition, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Payment condition not found")
    session.delete(condition)
    session.commit()
    return {"message": "Payment condition deleted"}

@router.put("/{condition_id}", response_model=PaymentConditionResponse)
def update_payment_condition(
    condition_id: int, 
    condition_data: PaymentConditionUpdate, 
    session: Session = Depends(get_session)
):
    # Get existing condition
    condition = session.get(PaymentCondition, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Payment condition not found")
    
    # Update the condition with new data (only provided fields)
    condition_dict = condition_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in condition_dict.items():
        setattr(condition, key, value)
    
    condition.updated_at = datetime.utcnow()
    session.add(condition)
    session.commit()
    session.refresh(condition)
    return condition 
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Budget, BudgetCreate, BudgetRead, BudgetUpdate, Client, Contact, Project
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[BudgetRead])
def get_budgets(session: Session = Depends(get_session)):
    """Get all budgets"""
    statement = select(Budget)
    results = session.exec(statement)
    return [{
        "id": budget.id,
        "number": budget.number,
        "name": budget.name,
        "client_id": budget.client_id,
        "contact_id": budget.contact_id,
        "delivery_date": budget.delivery_date,
        "created_at": budget.created_at,
        "updated_at": budget.updated_at
    } for budget in results]

@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, session: Session = Depends(get_session)):
    """Get a specific budget by ID"""
    statement = select(Budget).where(Budget.id == budget_id)
    result = session.exec(statement)
    budget = result.one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {
        "id": budget.id,
        "number": budget.number,
        "name": budget.name,
        "client_id": budget.client_id,
        "contact_id": budget.contact_id,
        "delivery_date": budget.delivery_date,
        "created_at": budget.created_at,
        "updated_at": budget.updated_at
    }

@router.post("/", response_model=BudgetRead)
def create_budget(budget: BudgetCreate, session: Session = Depends(get_session)):
    """Create a new budget"""
    # Verify that the client exists
    client = session.get(Client, budget.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Verify that the contact exists
    contact = session.get(Contact, budget.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Verify that the contact belongs to the client
    if contact.client_id != client.id:
        raise HTTPException(
            status_code=400,
            detail="Contact does not belong to the specified client"
        )
    
    db_budget = Budget.model_validate(budget)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    
    return {
        "id": db_budget.id,
        "number": db_budget.number,
        "name": db_budget.name,
        "client_id": db_budget.client_id,
        "contact_id": db_budget.contact_id,
        "delivery_date": db_budget.delivery_date,
        "created_at": db_budget.created_at,
        "updated_at": db_budget.updated_at
    }

@router.put("/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, budget_data: BudgetUpdate, session: Session = Depends(get_session)):
    """Update a budget"""
    # Get the existing budget
    statement = select(Budget).where(Budget.id == budget_id)
    result = session.exec(statement)
    db_budget = result.one_or_none()
    
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # If client_id is being updated, verify that the new client exists
    if budget_data.client_id is not None and budget_data.client_id != db_budget.client_id:
        client = session.get(Client, budget_data.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
    
    # If contact_id is being updated, verify that the new contact exists
    if budget_data.contact_id is not None and budget_data.contact_id != db_budget.contact_id:
        contact = session.get(Contact, budget_data.contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # If client_id is also being updated, verify contact belongs to new client
        if budget_data.client_id is not None:
            if contact.client_id != budget_data.client_id:
                raise HTTPException(
                    status_code=400,
                    detail="Contact does not belong to the specified client"
                )
        # If client_id is not being updated, verify contact belongs to current client
        elif contact.client_id != db_budget.client_id:
            raise HTTPException(
                status_code=400,
                detail="Contact does not belong to the budget's client"
            )
    
    # Update the provided fields
    budget_data_dict = budget_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in budget_data_dict.items():
        setattr(db_budget, key, value)
    
    # Update the modification date
    db_budget.updated_at = datetime.utcnow()
    
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    
    return {
        "id": db_budget.id,
        "number": db_budget.number,
        "name": db_budget.name,
        "client_id": db_budget.client_id,
        "contact_id": db_budget.contact_id,
        "delivery_date": db_budget.delivery_date,
        "created_at": db_budget.created_at,
        "updated_at": db_budget.updated_at
    }

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, session: Session = Depends(get_session)):
    """Delete a budget"""
    # First check if the budget exists
    statement = select(Budget).where(Budget.id == budget_id)
    budget = session.exec(statement).one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Check if the budget is associated with any project
    if budget.project:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete budget that is associated with a project"
        )
    
    session.delete(budget)
    session.commit()
    return {"message": "Budget deleted"} 
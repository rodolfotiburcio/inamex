from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import RequirementState, RequirementStateCreate, RequirementStateResponse, RequirementStateUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[RequirementStateResponse])
def get_requirement_states(session: Session = Depends(get_session)):
    statement = select(RequirementState)
    results = session.exec(statement)
    return [{
        "id": state.id,
        "name": state.name,
        "description": state.description
    } for state in results]
    
@router.get("/{state_id}", response_model=RequirementStateResponse)
def get_requirement_state(state_id: int, session: Session = Depends(get_session)):
    statement = select(RequirementState).where(RequirementState.id == state_id)
    result = session.exec(statement)
    state = result.one_or_none()
    if not state:
        raise HTTPException(status_code=404, detail="Requirement state not found")
    return {
        "id": state.id,
        "name": state.name,
        "description": state.description
    }
    
@router.delete("/{state_id}")
def delete_requirement_state(state_id: int, session: Session = Depends(get_session)):
    statement = delete(RequirementState).where(RequirementState.id == state_id)
    session.exec(statement)
    session.commit()
    return {"message": "Requirement state deleted"}

@router.post("/", response_model=RequirementStateResponse)
def create_requirement_state(state: RequirementStateCreate, session: Session = Depends(get_session)):
    db_state = RequirementState.model_validate(state)
    session.add(db_state)
    session.commit()
    session.refresh(db_state)
    return {
        "id": db_state.id,
        "name": db_state.name,
        "description": db_state.description,
        "order": db_state.order,
        "active": db_state.active
    }

@router.put("/{state_id}", response_model=RequirementStateResponse)
def update_requirement_state(
    state_id: int, 
    state_data: RequirementStateUpdate, 
    session: Session = Depends(get_session)
):
    # Get existing state
    statement = select(RequirementState).where(RequirementState.id == state_id)
    result = session.exec(statement)
    db_state = result.one_or_none()
    
    if not db_state:
        raise HTTPException(status_code=404, detail="Requirement state not found")
    
    # Update the state with new data (only provided fields)
    state_dict = state_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in state_dict.items():
        setattr(db_state, key, value)
    
    db_state.updated_at = datetime.utcnow()
    session.add(db_state)
    session.commit()
    session.refresh(db_state)
    
    return {
        "id": db_state.id,
        "name": db_state.name,
        "description": db_state.description,
        "order": db_state.order,
        "active": db_state.active,
        "created_at": db_state.created_at,
        "updated_at": db_state.updated_at
    }
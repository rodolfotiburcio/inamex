from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import ProjectState, ProjectStateCreate, ProjectStateResponse, ProjectStateUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ProjectStateResponse])
def get_project_states(session: Session = Depends(get_session)):
    statement = select(ProjectState)
    results = session.exec(statement)
    return [{
        "id": state.id,
        "name": state.name,
        "description": state.description,
        "order": state.order,
        "active": state.active,
        "created_at": state.created_at,
        "updated_at": state.updated_at
    } for state in results]
    
@router.get("/{state_id}", response_model=ProjectStateResponse)
def get_project_state(state_id: int, session: Session = Depends(get_session)):
    statement = select(ProjectState).where(ProjectState.id == state_id)
    result = session.exec(statement)
    state = result.one_or_none()
    if not state:
        raise HTTPException(status_code=404, detail="Project state not found")
    return {
        "id": state.id,
        "name": state.name,
        "description": state.description,
        "order": state.order,
        "active": state.active,
        "created_at": state.created_at,
        "updated_at": state.updated_at
    }
    
@router.delete("/{state_id}")
def delete_project_state(state_id: int, session: Session = Depends(get_session)):
    statement = delete(ProjectState).where(ProjectState.id == state_id)
    session.exec(statement)
    session.commit()
    return {"message": "Project state deleted"}

@router.post("/", response_model=ProjectStateResponse)
def create_project_state(state: ProjectStateCreate, session: Session = Depends(get_session)):
    db_state = ProjectState.model_validate(state)
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

@router.put("/{state_id}", response_model=ProjectStateResponse)
def update_project_state(state_id: int, state_data: ProjectStateUpdate, session: Session = Depends(get_session)):
    # Obtener el estado de proyecto existente
    statement = select(ProjectState).where(ProjectState.id == state_id)
    result = session.exec(statement)
    db_state = result.one_or_none()
    
    if not db_state:
        raise HTTPException(status_code=404, detail="Project state not found")
    
    # Si se actualiza el nombre, verificar que no exista ya otro estado con ese nombre
    if state_data.name is not None and state_data.name != db_state.name:
        name_check = select(ProjectState).where(ProjectState.name == state_data.name)
        existing_state = session.exec(name_check).first()
        if existing_state:
            raise HTTPException(status_code=400, detail="Project state name already exists")
    
    # Actualizar los campos proporcionados
    state_data_dict = state_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in state_data_dict.items():
        setattr(db_state, key, value)
    
    # Actualizar la fecha de modificación
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
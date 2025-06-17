from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import Project, ProjectCreate, ProjectResponse, ProjectUpdate, User, Client, ProjectState
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ProjectResponse])
def get_projects(session: Session = Depends(get_session)):
    statement = select(Project)
    results = session.exec(statement)
    projects = [{
        "id": project.id,
        "number": project.number,
        "name": project.name,
        "description": project.description,
        "date": project.date,
        "state_id": project.state_id,
        "responsible_id": project.responsible_id,
        "client_id": project.client_id
    } for project in results]
    return projects
    
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, session: Session = Depends(get_session)):
    statement = select(Project).where(Project.id == project_id)
    result = session.exec(statement)
    project = result.one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": project.id,
        "number": project.number,
        "name": project.name,
        "description": project.description,
        "date": project.date,
        "state_id": project.state_id,
        "responsible_id": project.responsible_id,
        "client_id": project.client_id
    }
    
@router.delete("/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    # Verificar si el proyecto existe
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    session.delete(project)
    session.commit()
    
    return {"message": "Project deleted"}

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, session: Session = Depends(get_session)):
    print(project)
    # Verify that the referenced entities exist
    if project.state_id:
        state = session.get(ProjectState, project.state_id)
        if not state:
            raise HTTPException(status_code=400, detail="Invalid state_id")
    
    if project.responsible_id:
        user = session.get(User, project.responsible_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid responsible_id")
    
    if project.client_id:
        client = session.get(Client, project.client_id)
        if not client:
            raise HTTPException(status_code=400, detail="Invalid client_id")
    
    db_project = Project.model_validate(project)
    
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    
    return {
        "id": db_project.id,
        "number": db_project.number,
        "name": db_project.name,
        "description": db_project.description,
        "date": db_project.date,
        "state_id": db_project.state_id,
        "responsible_id": db_project.responsible_id,
        "client_id": db_project.client_id
    }

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int, 
    project_data: ProjectUpdate, 
    session: Session = Depends(get_session)
):
    # Get existing project
    statement = select(Project).where(Project.id == project_id)
    result = session.exec(statement)
    db_project = result.one_or_none()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify that the referenced entities exist if they are being updated
    if project_data.state_id is not None:
        state = session.get(ProjectState, project_data.state_id)
        if not state:
            raise HTTPException(status_code=400, detail="Invalid state_id")
    
    if project_data.responsible_id is not None:
        user = session.get(User, project_data.responsible_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid responsible_id")
    
    if project_data.client_id is not None:
        client = session.get(Client, project_data.client_id)
        if not client:
            raise HTTPException(status_code=400, detail="Invalid client_id")
    
    # Verificar si se actualiza el número y que no exista otro proyecto con ese número
    if project_data.number is not None and project_data.number != db_project.number:
        number_check = select(Project).where(Project.number == project_data.number)
        existing_project = session.exec(number_check).first()
        if existing_project:
            raise HTTPException(status_code=400, detail="Project number already exists")
    
    # Update the project with new data (only provided fields)
    project_dict = project_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in project_dict.items():
        setattr(db_project, key, value)
    
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    
    return {
        "id": db_project.id,
        "number": db_project.number,
        "name": db_project.name,
        "description": db_project.description,
        "date": db_project.date,
        "state_id": db_project.state_id,
        "responsible_id": db_project.responsible_id,
        "client_id": db_project.client_id
    } 
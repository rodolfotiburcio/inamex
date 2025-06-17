from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import (
    Client, ClientCreate, ClientResponse, ClientUpdate, 
    ProjectBasicResponse, ContactBasicResponse, BudgetBasicResponse,
    FullClientResponse
)
from datetime import datetime
from typing import List

router = APIRouter()

@router.get("/", response_model=list[ClientResponse])
def get_clients(session: Session = Depends(get_session)):
    statement = select(Client)
    results = session.exec(statement)
    return [{
        "id": client.id,
        "name": client.name,
        "created_at": client.created_at,
        "updated_at": client.updated_at
    } for client in results]
    
@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, session: Session = Depends(get_session)):
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement)
    client = result.one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get client's projects
    projects = []
    for project in client.projects:
        projects.append({
            "id": project.id,
            "name": project.name
        })
    
    return {
        "id": client.id,
        "name": client.name,
        "created_at": client.created_at,
        "updated_at": client.updated_at,
        "projects": projects
    }

@router.get("/fullclient/{client_id}", response_model=FullClientResponse)
def get_full_client(client_id: int, session: Session = Depends(get_session)):
    # Get the client
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement)
    client = result.one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get latest 5 projects
    projects = sorted(client.projects, key=lambda x: x.date, reverse=True)[:5]
    latest_projects = [
        ProjectBasicResponse(
            id=project.id,
            name=project.name,
            number=project.number,
            date=project.date,
            state_id=project.state_id
        ) for project in projects
    ]
    
    # Get latest 5 contacts
    contacts = sorted(client.contacts, key=lambda x: x.created_at, reverse=True)[:5]
    latest_contacts = [
        ContactBasicResponse(
            id=contact.id,
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            position=contact.position
        ) for contact in contacts
    ]
    
    # Get latest 5 budgets
    budgets = sorted(client.budgets, key=lambda x: x.created_at, reverse=True)[:5]
    latest_budgets = [
        BudgetBasicResponse(
            id=budget.id,
            name=budget.name,
            delivery_date=budget.delivery_date,
            contact_id=budget.contact_id
        ) for budget in budgets
    ]
    
    return {
        "id": client.id,
        "name": client.name,
        "created_at": client.created_at,
        "updated_at": client.updated_at,
        "latest_projects": latest_projects,
        "latest_contacts": latest_contacts,
        "latest_budgets": latest_budgets
    }

@router.post("/", response_model=ClientResponse)
def create_client(client: ClientCreate, session: Session = Depends(get_session)):
    db_client = Client.model_validate(client)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return {
        "id": db_client.id,
        "name": db_client.name,
        "created_at": db_client.created_at,
        "updated_at": db_client.updated_at
    }

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_update: ClientUpdate, session: Session = Depends(get_session)):
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement)
    client = result.one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # If name is being updated, check if it conflicts with existing client
    if client_update.name is not None and client_update.name != client.name:
        existing_client = session.exec(
            select(Client).where(Client.name == client_update.name)
        ).one_or_none()
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="Client name already exists"
            )
    
    client_data = client_update.model_dump(exclude_unset=True)
    for key, value in client_data.items():
        setattr(client, key, value)
    
    client.updated_at = datetime.utcnow()
    session.add(client)
    session.commit()
    session.refresh(client)
    return {
        "id": client.id,
        "name": client.name,
        "created_at": client.created_at,
        "updated_at": client.updated_at
    }

@router.delete("/{client_id}")
def delete_client(client_id: int, session: Session = Depends(get_session)):
    statement = select(Client).where(Client.id == client_id)
    result = session.exec(statement)
    client = result.one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    session.delete(client)
    session.commit()
    return {"message": "Client deleted"} 
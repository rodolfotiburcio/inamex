from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import Contact, ContactCreate, ContactRead, ContactUpdate, Client
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ContactRead])
def get_contacts(session: Session = Depends(get_session)):
    statement = select(Contact)
    results = session.exec(statement)
    return [{
        "id": contact.id,
        "name": contact.name,
        "email": contact.email,
        "phone": contact.phone,
        "position": contact.position,
        "client_id": contact.client_id,
        "created_at": contact.created_at,
        "updated_at": contact.updated_at
    } for contact in results]

@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, session: Session = Depends(get_session)):
    statement = select(Contact).where(Contact.id == contact_id)
    result = session.exec(statement)
    contact = result.one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return {
        "id": contact.id,
        "name": contact.name,
        "email": contact.email,
        "phone": contact.phone,
        "position": contact.position,
        "client_id": contact.client_id,
        "created_at": contact.created_at,
        "updated_at": contact.updated_at
    }

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    # First check if the contact exists
    statement = select(Contact).where(Contact.id == contact_id)
    contact = session.exec(statement).one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    session.delete(contact)
    session.commit()
    return {"message": "Contact deleted"}

@router.post("/", response_model=ContactRead)
def create_contact(contact: ContactCreate, session: Session = Depends(get_session)):
    # Verify that the client exists
    client = session.get(Client, contact.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_contact = Contact.model_validate(contact)
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return {
        "id": db_contact.id,
        "name": db_contact.name,
        "email": db_contact.email,
        "phone": db_contact.phone,
        "position": db_contact.position,
        "client_id": db_contact.client_id,
        "created_at": db_contact.created_at,
        "updated_at": db_contact.updated_at
    }

@router.put("/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: int, contact_data: ContactUpdate, session: Session = Depends(get_session)):
    # Get the existing contact
    statement = select(Contact).where(Contact.id == contact_id)
    result = session.exec(statement)
    db_contact = result.one_or_none()
    
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # If client_id is being updated, verify that the new client exists
    if contact_data.client_id is not None and contact_data.client_id != db_contact.client_id:
        client = session.get(Client, contact_data.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
    
    # Update the provided fields
    contact_data_dict = contact_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in contact_data_dict.items():
        setattr(db_contact, key, value)
    
    # Update the modification date
    db_contact.updated_at = datetime.utcnow()
    
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    
    return {
        "id": db_contact.id,
        "name": db_contact.name,
        "email": db_contact.email,
        "phone": db_contact.phone,
        "position": db_contact.position,
        "client_id": db_contact.client_id,
        "created_at": db_contact.created_at,
        "updated_at": db_contact.updated_at
    } 
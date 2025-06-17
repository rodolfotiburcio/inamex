from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import Address, AddressCreate, AddressResponse, AddressUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[AddressResponse])
def get_addresses(session: Session = Depends(get_session)):
    """Get all addresses"""
    statement = select(Address)
    results = session.exec(statement)
    return [{
        "id": address.id,
        "street": address.street,
        "exterior_number": address.exterior_number,
        "interior_number": address.interior_number,
        "neighborhood": address.neighborhood,
        "postal_code": address.postal_code,
        "city": address.city,
        "state": address.state,
        "country": address.country,
        "notes": address.notes
    } for address in results]

@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, session: Session = Depends(get_session)):
    """Get a specific address by ID"""
    statement = select(Address).where(Address.id == address_id)
    result = session.exec(statement)
    address = result.one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return {
        "id": address.id,
        "street": address.street,
        "exterior_number": address.exterior_number,
        "interior_number": address.interior_number,
        "neighborhood": address.neighborhood,
        "postal_code": address.postal_code,
        "city": address.city,
        "state": address.state,
        "country": address.country,
        "notes": address.notes
    }

@router.post("/", response_model=AddressResponse)
def create_address(address: AddressCreate, session: Session = Depends(get_session)):
    """Create a new address"""
    db_address = Address.model_validate(address)
    session.add(db_address)
    session.commit()
    session.refresh(db_address)
    return {
        "id": db_address.id,
        "street": db_address.street,
        "exterior_number": db_address.exterior_number,
        "interior_number": db_address.interior_number,
        "neighborhood": db_address.neighborhood,
        "postal_code": db_address.postal_code,
        "city": db_address.city,
        "state": db_address.state,
        "country": db_address.country,
        "notes": db_address.notes
    }

@router.put("/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, address_update: AddressUpdate, session: Session = Depends(get_session)):
    """Update an existing address"""
    # Get the existing address
    statement = select(Address).where(Address.id == address_id)
    result = session.exec(statement)
    address = result.one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Update only the fields that were provided
    update_data = address_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    # Update the updated_at timestamp
    address.updated_at = datetime.utcnow()

    session.add(address)
    session.commit()
    session.refresh(address)

    return {
        "id": address.id,
        "street": address.street,
        "exterior_number": address.exterior_number,
        "interior_number": address.interior_number,
        "neighborhood": address.neighborhood,
        "postal_code": address.postal_code,
        "city": address.city,
        "state": address.state,
        "country": address.country,
        "notes": address.notes
    }

@router.delete("/{address_id}")
def delete_address(address_id: int, session: Session = Depends(get_session)):
    """Delete an address"""
    # First check if the address is being used by any supplier
    statement = select(Address).where(Address.id == address_id)
    address = session.exec(statement).one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Check if the address has any suppliers
    if address.suppliers:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete address that is being used by suppliers"
        )
    
    statement = delete(Address).where(Address.id == address_id)
    session.exec(statement)
    session.commit()
    return {"message": "Address deleted"} 
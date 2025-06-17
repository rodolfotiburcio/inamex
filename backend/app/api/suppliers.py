from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import Supplier, SupplierCreate, SupplierResponse, SupplierUpdate, Address, PaymentCondition
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(session: Session = Depends(get_session)):
    statement = select(Supplier)
    results = session.exec(statement)
    return [{
        "id": supplier.id,
        "rfc": supplier.rfc,
        "name": supplier.name,
        "address_id": supplier.address_id,
        "bank_details": supplier.bank_details,
        "delivery_time": supplier.delivery_time,
        "payment_condition_id": supplier.payment_condition_id,
        "currency": supplier.currency,
        "notes": supplier.notes
    } for supplier in results]
    
@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, session: Session = Depends(get_session)):
    statement = select(Supplier).where(Supplier.id == supplier_id)
    result = session.exec(statement)
    supplier = result.one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {
        "id": supplier.id,
        "rfc": supplier.rfc,    
        "name": supplier.name,
        "address_id": supplier.address_id,
        "bank_details": supplier.bank_details,
        "delivery_time": supplier.delivery_time,
        "payment_condition_id": supplier.payment_condition_id,
        "currency": supplier.currency,
        "notes": supplier.notes
    }
    
@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, session: Session = Depends(get_session)):
    statement = delete(Supplier).where(Supplier.id == supplier_id)
    session.exec(statement)
    session.commit()
    return {"message": "Supplier deleted"}

@router.post("/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, session: Session = Depends(get_session)):
    db_supplier = Supplier.model_validate(supplier)
    session.add(db_supplier)
    session.commit()
    session.refresh(db_supplier)
    return {
        "id": db_supplier.id,
        "rfc": db_supplier.rfc,
        "name": db_supplier.name,
        "address_id": db_supplier.address_id,
        "bank_details": db_supplier.bank_details,
        "delivery_time": db_supplier.delivery_time,
        "payment_condition_id": db_supplier.payment_condition_id,
        "currency": db_supplier.currency,
        "notes": db_supplier.notes
    }

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier_update: SupplierUpdate, session: Session = Depends(get_session)):
    # Get the existing supplier
    statement = select(Supplier).where(Supplier.id == supplier_id)
    result = session.exec(statement)
    supplier = result.one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Verify that the address exists if being updated
    if supplier_update.address_id is not None:
        address = session.get(Address, supplier_update.address_id)
        if not address:
            raise HTTPException(status_code=400, detail="Address not found")

    # Verify that the payment condition exists if being updated
    if supplier_update.payment_condition_id is not None:
        payment_condition = session.get(PaymentCondition, supplier_update.payment_condition_id)
        if not payment_condition:
            raise HTTPException(status_code=400, detail="Payment condition not found")

    # Update only the fields that were provided
    update_data = supplier_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    # Update the updated_at timestamp
    supplier.updated_at = datetime.utcnow()

    session.add(supplier)
    session.commit()
    session.refresh(supplier)

    return {
        "id": supplier.id,
        "rfc": supplier.rfc,
        "name": supplier.name,
        "address_id": supplier.address_id,
        "bank_details": supplier.bank_details,
        "delivery_time": supplier.delivery_time,
        "payment_condition_id": supplier.payment_condition_id,
        "currency": supplier.currency,
        "notes": supplier.notes
    }

# @router.get("/{supplier_id}", response_model=SupplierResponse)
# def get_supplier(supplier_id: int, session: Session = get_session):
#     """Get a specific supplier by ID"""
#     supplier = session.get(Supplier, supplier_id)
#     if not supplier:
#         raise HTTPException(status_code=404, detail="Supplier not found")
#     return supplier

# @router.post("/", response_model=SupplierResponse)
# def create_supplier(supplier: SupplierCreate, session: Session = get_session):
#     """Create a new supplier"""
#     db_supplier = Supplier.from_orm(supplier)
#     session.add(db_supplier)
#     session.commit()
#     session.refresh(db_supplier)
#     return db_supplier

# @router.delete("/{supplier_id}")
# def delete_supplier(supplier_id: int, session: Session = get_session):
#     """Delete a supplier"""
#     supplier = session.get(Supplier, supplier_id)
#     if not supplier:
#         raise HTTPException(status_code=404, detail="Supplier not found")
#     session.delete(supplier)
#     session.commit()
#     return {"message": "Supplier deleted"} 
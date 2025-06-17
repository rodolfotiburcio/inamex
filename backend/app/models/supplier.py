from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class SupplierBase(SQLModel):
    name: str
    rfc: str = Field(unique=True, index=True)
    address_id: int = Field(foreign_key="address.id")
    bank_details: str
    delivery_time: str
    payment_condition_id: int = Field(foreign_key="paymentcondition.id")
    currency: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Supplier(SupplierBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    payment_condition: "PaymentCondition" = Relationship(back_populates="suppliers")
    address: "Address" = Relationship(back_populates="suppliers")
    orders: List["Order"] = Relationship(back_populates="supplier")

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SQLModel):
    name: Optional[str] = None
    rfc: Optional[str] = None
    address_id: Optional[int] = None
    bank_details: Optional[str] = None
    delivery_time: Optional[str] = None
    payment_condition_id: Optional[int] = None
    currency: Optional[str] = None
    notes: Optional[str] = None

class SupplierResponse(SupplierBase):
    id: int 
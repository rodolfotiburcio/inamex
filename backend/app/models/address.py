from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class AddressBase(SQLModel):
    street: str
    exterior_number: str
    interior_number: Optional[str] = None
    neighborhood: str
    postal_code: str
    city: str
    state: str
    country: str = "México"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Address(AddressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    suppliers: List["Supplier"] = Relationship(back_populates="address")
    orders: List["Order"] = Relationship(back_populates="shipping_address")

class AddressCreate(AddressBase):
    pass

class AddressUpdate(SQLModel):
    street: Optional[str] = None
    exterior_number: Optional[str] = None
    interior_number: Optional[str] = None
    neighborhood: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None

class AddressResponse(AddressBase):
    id: int 
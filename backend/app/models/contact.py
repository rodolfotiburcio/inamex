from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from app.models.client import Client

class ContactBase(SQLModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    client_id: int = Field(foreign_key="client.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Contact(ContactBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    client: "Client" = Relationship(back_populates="contacts")
    budgets: List["Budget"] = Relationship(back_populates="contact")

class ContactCreate(ContactBase):
    pass

class ContactRead(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ContactUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    client_id: Optional[int] = None 
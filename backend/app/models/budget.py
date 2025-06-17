from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from app.models.client import Client
from app.models.contact import Contact

class BudgetBase(SQLModel):
    number: int
    name: str
    client_id: int = Field(foreign_key="client.id")
    contact_id: int = Field(foreign_key="contact.id")
    delivery_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    client: Client = Relationship(back_populates="budgets")
    contact: Contact = Relationship(back_populates="budgets")
    project: Optional["Project"] = Relationship(back_populates="budget")

class BudgetCreate(BudgetBase):
    pass

class BudgetRead(BudgetBase):
    id: int
    created_at: datetime
    updated_at: datetime

class BudgetUpdate(SQLModel):
    number: Optional[int] = None
    name: Optional[str] = None
    client_id: Optional[int] = None
    contact_id: Optional[int] = None
    delivery_date: Optional[datetime] = None 
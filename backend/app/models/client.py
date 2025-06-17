from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class ClientBase(SQLModel):
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="client")
    contacts: List["Contact"] = Relationship(back_populates="client")
    budgets: List["Budget"] = Relationship(back_populates="client")

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ClientUpdate(SQLModel):
    name: Optional[str] = None

class ProjectBasicResponse(SQLModel):
    id: int
    name: str
    number: str
    date: datetime
    state_id: int

class ContactBasicResponse(SQLModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None

class BudgetBasicResponse(SQLModel):
    id: int
    name: str
    delivery_date: datetime
    contact_id: int

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

class FullClientResponse(ClientResponse):
    latest_projects: List[ProjectBasicResponse]
    latest_contacts: List[ContactBasicResponse]
    latest_budgets: List[BudgetBasicResponse]
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    full_name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="responsible")
    requested_requirements: List["Requirement"] = Relationship(back_populates="requester")
    accepted_orders: List["Order"] = Relationship(back_populates="accepted_by", sa_relationship_kwargs={"foreign_keys": "[Order.acceptance_id]"})
    requested_orders: List["Order"] = Relationship(back_populates="requested_by", sa_relationship_kwargs={"foreign_keys": "[Order.requested_by_id]"})
    reviewed_orders: List["Order"] = Relationship(back_populates="reviewed_by", sa_relationship_kwargs={"foreign_keys": "[Order.reviewed_by_id]"})
    approved_orders: List["Order"] = Relationship(back_populates="approved_by", sa_relationship_kwargs={"foreign_keys": "[Order.approved_by_id]"})
    reports: List["Report"] = Relationship(back_populates="responsible")
    dedicated_times: List["DedicatedTime"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int 

class UserUpdate(SQLModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    password_hash: Optional[str] = None 
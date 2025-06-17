from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class RequirementStateBase(SQLModel):
    name: str
    description: Optional[str] = None
    order: int = Field(default=0)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RequirementState(RequirementStateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    requirements: List["Requirement"] = Relationship(back_populates="state")

class RequirementStateCreate(RequirementStateBase):
    pass

class RequirementStateResponse(RequirementStateBase):
    id: int

class RequirementStateUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None
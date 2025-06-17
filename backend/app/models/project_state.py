from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class ProjectStateBase(SQLModel):
    name: str
    description: Optional[str] = None
    order: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectState(ProjectStateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="state")

class ProjectStateCreate(ProjectStateBase):
    pass

class ProjectStateResponse(ProjectStateBase):
    id: int 

class ProjectStateUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None 
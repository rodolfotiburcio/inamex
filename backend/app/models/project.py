from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class ProjectBase(SQLModel):
    number: str
    name: str
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    state_id: int = Field(foreign_key="projectstate.id")
    responsible_id: Optional[int] = Field(foreign_key="user.id", default=None)
    client_id: Optional[int] = Field(foreign_key="client.id", default=None)
    budget_id: Optional[int] = Field(foreign_key="budget.id", default=None)

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    state: "ProjectState" = Relationship(back_populates="projects")
    responsible: Optional["User"] = Relationship(back_populates="projects")
    client: Optional["Client"] = Relationship(back_populates="projects")
    requirements: List["Requirement"] = Relationship(back_populates="project")
    reports: List["Report"] = Relationship(back_populates="project")
    budget: Optional["Budget"] = Relationship(back_populates="project")
    
class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int 

class ProjectUpdate(SQLModel):
    number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    state_id: Optional[int] = None
    responsible_id: Optional[int] = None
    client_id: Optional[int] = None 
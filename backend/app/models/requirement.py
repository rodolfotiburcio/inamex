from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from .article import ArticleCreate
from decimal import Decimal

class RequirementBase(SQLModel):
    project_id: Optional[int] = Field(foreign_key="project.id", default=None)
    request_date: datetime = Field(default_factory=datetime.utcnow)
    requested_by: Optional[int] = Field(foreign_key="user.id", default=None)
    state_id: int = Field(foreign_key="requirementstate.id")
    closing_date: Optional[datetime] = None

class Requirement(RequirementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    project: Optional["Project"] = Relationship(back_populates="requirements")
    requester: Optional["User"] = Relationship(back_populates="requested_requirements")
    state: "RequirementState" = Relationship(back_populates="requirements")
    articles: List["Article"] = Relationship(back_populates="requirement")

class RequirementCreate(RequirementBase):
    pass

class RequirementResponse(RequirementBase):
    id: int

class RequirementWithArticlesCreate(SQLModel):
    """Model for creating a requirement with its articles"""
    requirement: RequirementCreate
    articles: List["ArticleCreateWithoutRequirement"]

class ArticleCreateWithoutRequirement(SQLModel):
    """Model for creating an article without requirement_id"""
    quantity: Decimal
    unit: str
    brand: str
    model: str
    dimensions: str
    state_id: int = Field(foreign_key="articlestate.id")
    notes: Optional[str] = None 
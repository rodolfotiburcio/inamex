from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ArticleBase(SQLModel):
    requirement_id: Optional[int] = Field(foreign_key="requirement.id", default=None)
    requirement_consecutive: Optional[int] = None
    quantity: Decimal
    unit: str
    brand: str
    model: str
    dimensions: str
    state_id: int = Field(foreign_key="articlestate.id")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    requirement: Optional["Requirement"] = Relationship(back_populates="articles")
    state: "ArticleState" = Relationship(back_populates="articles")
    article_orders: List["ArticleOrder"] = Relationship(back_populates="article")

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int

class ArticleUpdate(SQLModel):
    requirement_id: Optional[int] = None
    requirement_consecutive: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    dimensions: Optional[str] = None
    state_id: Optional[int] = None
    notes: Optional[str] = None 
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class ArticleOrderStatusBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    order: int = Field(default=0)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ArticleOrderStatus(ArticleOrderStatusBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    articles: List["ArticleOrder"] = Relationship(back_populates="status")

class ArticleOrderStatusCreate(ArticleOrderStatusBase):
    pass

class ArticleOrderStatusResponse(ArticleOrderStatusBase):
    id: int

class ArticleOrderStatusUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None 
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class ArticleStateBase(SQLModel):
    name: str
    description: Optional[str] = None
    order: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ArticleState(ArticleStateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    articles: List["Article"] = Relationship(back_populates="state")

class ArticleStateCreate(ArticleStateBase):
    pass

class ArticleStateResponse(ArticleStateBase):
    id: int

class ArticleStateUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None 
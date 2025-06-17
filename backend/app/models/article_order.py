from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ArticleOrderBase(SQLModel):
    order_id: int = Field(foreign_key="order.id")
    article_req_id: Optional[int] = Field(foreign_key="article.id", default=None)
    status_id: int = Field(foreign_key="articleorderstatus.id")
    position: int
    quantity: Decimal
    unit: str
    brand: str
    model: str
    unit_price: Decimal
    total: Decimal
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ArticleOrder(ArticleOrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    order: "Order" = Relationship(back_populates="articles")
    article: Optional["Article"] = Relationship(back_populates="article_orders")
    status: "ArticleOrderStatus" = Relationship(back_populates="articles")

class ArticleOrderCreate(ArticleOrderBase):
    pass

class ArticleOrderResponse(ArticleOrderBase):
    id: int

class ArticleOrderUpdate(SQLModel):
    order_id: Optional[int] = None
    article_req_id: Optional[int] = None
    status_id: Optional[int] = None
    position: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None
    notes: Optional[str] = None 
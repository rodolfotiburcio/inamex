from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class OrderStatusBase(SQLModel):
    name: str
    description: Optional[str] = None
    order: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderStatus(OrderStatusBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="status")

class OrderStatusCreate(OrderStatusBase):
    pass

class OrderStatusResponse(OrderStatusBase):
    id: int

class OrderStatusUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None 
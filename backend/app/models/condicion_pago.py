from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from sqlmodel import Relationship

class PaymentCondition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    text: str
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    suppliers: List["Supplier"] = Relationship(back_populates="payment_condition")
    orders: List["Order"] = Relationship(back_populates="payment_condition")

class PaymentConditionCreate(SQLModel):
    name: str
    description: Optional[str] = None
    text: str
    active: Optional[bool] = True

class PaymentConditionResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    text: str
    active: bool
    created_at: datetime
    updated_at: datetime

class PaymentConditionUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    active: Optional[bool] = None 
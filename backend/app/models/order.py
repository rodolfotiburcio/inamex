from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class OrderBase(SQLModel):
    supplier_id: int = Field(foreign_key="supplier.id")
    address: str
    bank_details: str
    date: datetime = Field(default_factory=datetime.utcnow)
    delivery_time: str
    payment_condition_id: int = Field(foreign_key="paymentcondition.id")
    currency: str
    supplier_reference: Optional[str] = None
    acceptance_id: Optional[int] = Field(foreign_key="user.id", default=None)
    requested_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    approved_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    subtotal: Decimal
    vat: Decimal
    discount: Decimal = Field(default=0)
    total: Decimal
    notes: Optional[str] = None
    shipping_address_id: int = Field(foreign_key="address.id")
    status_id: int = Field(foreign_key="orderstatus.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    supplier: "Supplier" = Relationship(back_populates="orders")
    payment_condition: "PaymentCondition" = Relationship(back_populates="orders")
    shipping_address: "Address" = Relationship(back_populates="orders")
    status: "OrderStatus" = Relationship(back_populates="orders")
    accepted_by: Optional["User"] = Relationship(back_populates="accepted_orders", sa_relationship_kwargs={"foreign_keys": "[Order.acceptance_id]"})
    requested_by: Optional["User"] = Relationship(back_populates="requested_orders", sa_relationship_kwargs={"foreign_keys": "[Order.requested_by_id]"})
    reviewed_by: Optional["User"] = Relationship(back_populates="reviewed_orders", sa_relationship_kwargs={"foreign_keys": "[Order.reviewed_by_id]"})
    approved_by: Optional["User"] = Relationship(back_populates="approved_orders", sa_relationship_kwargs={"foreign_keys": "[Order.approved_by_id]"})
    articles: List["ArticleOrder"] = Relationship(back_populates="order")


class OrderCreate(OrderBase):
    pass

class OrderUpdate(SQLModel):
    supplier_id: Optional[int] = None
    address: Optional[str] = None
    bank_details: Optional[str] = None
    date: Optional[datetime] = None
    delivery_time: Optional[str] = None
    payment_condition_id: Optional[int] = None
    currency: Optional[str] = None
    supplier_reference: Optional[str] = None
    acceptance_id: Optional[int] = None
    requested_by_id: Optional[int] = None
    reviewed_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    subtotal: Optional[Decimal] = None
    vat: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    total: Optional[Decimal] = None
    notes: Optional[str] = None
    shipping_address_id: Optional[int] = None
    status_id: Optional[int] = None

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

class OrderWithArticlesCreate(SQLModel):
    """Model for creating an order with its article orders"""
    order: OrderCreate
    articles: List["ArticleOrderCreateWithoutOrder"]

class ArticleOrderCreateWithoutOrder(SQLModel):
    """Model for creating an article order without order_id"""
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
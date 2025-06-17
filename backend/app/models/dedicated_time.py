from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime, timedelta

class DedicatedTimeBase(SQLModel):
    """Base model for dedicated time to a report by a user"""
    user_id: int = Field(foreign_key="user.id")
    time: timedelta
    report_id: int = Field(foreign_key="report.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DedicatedTime(DedicatedTimeBase, table=True):
    """Model for dedicated time to a report by a user"""
    __tablename__ = "dedicated_time"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="dedicated_times")
    report: Optional["Report"] = Relationship(back_populates="dedicated_times")

class DedicatedTimeCreate(DedicatedTimeBase):
    """Model for creating a dedicated time"""
    pass

class DedicatedTimeResponse(DedicatedTimeBase):
    """Model for dedicated time response"""
    id: int
    created_at: datetime
    updated_at: datetime

class DedicatedTimeUpdate(SQLModel):
    """Model for updating a dedicated time"""
    time: Optional[timedelta] = None
    user_id: Optional[int] = None
    report_id: Optional[int] = None 
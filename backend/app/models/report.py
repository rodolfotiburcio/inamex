from datetime import datetime, timedelta
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class ReportBase(SQLModel):
    """Base model for reports"""
    title: str
    description: str
    duration: timedelta
    dead_time: timedelta
    dead_time_cause: Optional[str] = None
    project_id: Optional[int] = Field(foreign_key="project.id", default=None)
    responsible_id: Optional[int] = Field(foreign_key="user.id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Report(ReportBase, table=True):
    """Model for project reports"""
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    project: Optional["Project"] = Relationship(back_populates="reports")
    responsible: Optional["User"] = Relationship(back_populates="reports")
    dedicated_times: List["DedicatedTime"] = Relationship(back_populates="report")
    photos: List["Photo"] = Relationship(back_populates="report")

class ReportCreate(ReportBase):
    """Model for creating a report"""
    pass

class ReportResponse(ReportBase):
    """Model for report response"""
    id: int
    created_at: datetime
    updated_at: datetime

class ReportUpdate(SQLModel):
    """Model for updating a report"""
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[timedelta] = None
    dead_time: Optional[timedelta] = None
    dead_time_cause: Optional[str] = None
    project_id: Optional[int] = None
    responsible_id: Optional[int] = None
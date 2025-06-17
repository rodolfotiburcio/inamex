from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class PhotoBase(SQLModel):
    """Base model for report photos"""
    path: str
    thumbnail: str
    report_id: int = Field(foreign_key="report.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Photo(PhotoBase, table=True):
    """Model for report photos"""
    __tablename__ = "photo"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    report: Optional["Report"] = Relationship(back_populates="photos")

class PhotoCreate(PhotoBase):
    """Model for creating a photo"""
    pass

class PhotoResponse(PhotoBase):
    """Model for photo response"""
    id: int
    created_at: datetime
    updated_at: datetime 
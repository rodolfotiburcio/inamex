from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import DedicatedTime, DedicatedTimeCreate, DedicatedTimeResponse, DedicatedTimeUpdate, User, Report
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[DedicatedTimeResponse])
def get_dedicated_times(session: Session = Depends(get_session)):
    """Get all dedicated times"""
    statement = select(DedicatedTime)
    results = session.exec(statement)
    dedicated_times = results.all()
    return dedicated_times

@router.get("/{dedicated_time_id}", response_model=DedicatedTimeResponse)
def get_dedicated_time(dedicated_time_id: int, session: Session = Depends(get_session)):
    """Get a specific dedicated time by ID"""
    statement = select(DedicatedTime).where(DedicatedTime.id == dedicated_time_id)
    result = session.exec(statement)
    dedicated_time = result.first()
    if not dedicated_time:
        raise HTTPException(status_code=404, detail="Dedicated time not found")
    return dedicated_time

@router.post("/", response_model=DedicatedTimeResponse)
def create_dedicated_time(dedicated_time: DedicatedTimeCreate, session: Session = Depends(get_session)):
    """Create a new dedicated time"""
    # Verify user exists
    user_statement = select(User).where(User.id == dedicated_time.user_id)
    user_result = session.exec(user_statement)
    user = user_result.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify report exists
    report_statement = select(Report).where(Report.id == dedicated_time.report_id)
    report_result = session.exec(report_statement)
    report = report_result.first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create dedicated time
    db_dedicated_time = DedicatedTime.model_validate(dedicated_time)
    session.add(db_dedicated_time)
    session.commit()
    session.refresh(db_dedicated_time)
    return db_dedicated_time

@router.delete("/{dedicated_time_id}")
def delete_dedicated_time(dedicated_time_id: int, session: Session = Depends(get_session)):
    """Delete a dedicated time by ID"""
    statement = select(DedicatedTime).where(DedicatedTime.id == dedicated_time_id)
    result = session.exec(statement)
    dedicated_time = result.first()
    if not dedicated_time:
        raise HTTPException(status_code=404, detail="Dedicated time not found")
    
    session.delete(dedicated_time)
    session.commit()
    return {"message": "Dedicated time deleted"}

@router.put("/{dedicated_time_id}", response_model=DedicatedTimeResponse)
def update_dedicated_time(dedicated_time_id: int, dedicated_time_update: DedicatedTimeUpdate, session: Session = Depends(get_session)):
    """Update a dedicated time"""
    # Get the dedicated time
    statement = select(DedicatedTime).where(DedicatedTime.id == dedicated_time_id)
    result = session.exec(statement)
    dedicated_time = result.first()
    if not dedicated_time:
        raise HTTPException(status_code=404, detail="Dedicated time not found")

    # Validate related entities if they are being updated
    if dedicated_time_update.user_id is not None:
        user_statement = select(User).where(User.id == dedicated_time_update.user_id)
        user_result = session.exec(user_statement)
        user = user_result.first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid user_id")
    
    if dedicated_time_update.report_id is not None:
        report_statement = select(Report).where(Report.id == dedicated_time_update.report_id)
        report_result = session.exec(report_statement)
        report = report_result.first()
        if not report:
            raise HTTPException(status_code=400, detail="Invalid report_id")

    # Update dedicated time fields
    for field, value in dedicated_time_update.model_dump(exclude_unset=True).items():
        setattr(dedicated_time, field, value)
    
    # Update the updated_at timestamp
    dedicated_time.updated_at = datetime.utcnow()
    
    session.add(dedicated_time)
    session.commit()
    session.refresh(dedicated_time)
    
    return dedicated_time 
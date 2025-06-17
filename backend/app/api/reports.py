from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import (
    Report, ReportCreate, ReportResponse,
    ReportUpdate,
    Project, User
)
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ReportResponse])
def get_reports(session: Session = Depends(get_session)):
    statement = select(Report)
    results = session.exec(statement)
    reports = [{
        "id": report.id,
        "title": report.title,
        "description": report.description,
        "duration": report.duration,
        "dead_time": report.dead_time,
        "dead_time_cause": report.dead_time_cause,
        "project_id": report.project_id,
        "responsible_id": report.responsible_id,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    } for report in results]
    return reports

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, session: Session = Depends(get_session)):
    statement = select(Report).where(Report.id == report_id)
    result = session.exec(statement)
    report = result.one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": report.id,
        "title": report.title,
        "description": report.description,
        "duration": report.duration,
        "dead_time": report.dead_time,
        "dead_time_cause": report.dead_time_cause,
        "project_id": report.project_id,
        "responsible_id": report.responsible_id,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    }

@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate, session: Session = Depends(get_session)):
    # Validate related entities
    if report.project_id:
        project = session.get(Project, report.project_id)
        if not project:
            raise HTTPException(status_code=400, detail="Invalid project_id")
    if report.responsible_id:
        user = session.get(User, report.responsible_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid responsible_id")
    db_report = Report.model_validate(report)
    session.add(db_report)
    session.commit()
    session.refresh(db_report)
    return {
        "id": db_report.id,
        "title": db_report.title,
        "description": db_report.description,
        "duration": db_report.duration,
        "dead_time": db_report.dead_time,
        "dead_time_cause": db_report.dead_time_cause,
        "project_id": db_report.project_id,
        "responsible_id": db_report.responsible_id,
        "created_at": db_report.created_at,
        "updated_at": db_report.updated_at
    }

@router.delete("/{report_id}")
def delete_report(report_id: int, session: Session = Depends(get_session)):
    statement = delete(Report).where(Report.id == report_id)
    session.exec(statement)
    session.commit()
    return {"message": "Report deleted"}

@router.put("/{report_id}", response_model=ReportResponse)
def update_report(report_id: int, report_update: ReportUpdate, session: Session = Depends(get_session)):
    """Update a report"""
    # Get the report
    statement = select(Report).where(Report.id == report_id)
    result = session.exec(statement)
    report = result.one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Validate related entities if they are being updated
    if report_update.project_id is not None:
        project = session.get(Project, report_update.project_id)
        if not project:
            raise HTTPException(status_code=400, detail="Invalid project_id")
    
    if report_update.responsible_id is not None:
        user = session.get(User, report_update.responsible_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid responsible_id")

    # Update report fields
    for field, value in report_update.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    
    # Update the updated_at timestamp
    report.updated_at = datetime.utcnow()
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return {
        "id": report.id,
        "title": report.title,
        "description": report.description,
        "duration": report.duration,
        "dead_time": report.dead_time,
        "dead_time_cause": report.dead_time_cause,
        "project_id": report.project_id,
        "responsible_id": report.responsible_id,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    }
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import (
    Requirement, RequirementCreate, RequirementResponse, RequirementWithArticlesCreate,
    Project, User, RequirementState, Article, ArticleState, ArticleCreateWithoutRequirement
)
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=list[RequirementResponse])
def get_requirements(session: Session = Depends(get_session)):
    statement = select(Requirement)
    results = session.exec(statement)
    requirements = [{
        "id": requirement.id,
        "project_id": requirement.project_id,
        "request_date": requirement.request_date,
        "requested_by_id": requirement.requested_by,
        "state_id": requirement.state_id,
        "closing_date": requirement.closing_date,
        "articles": requirement.articles
    } for requirement in results]
    return requirements
    
@router.get("/{requirement_id}", response_model=RequirementResponse)
def get_requirement(requirement_id: int, session: Session = Depends(get_session)):
    statement = select(Requirement).where(Requirement.id == requirement_id)
    result = session.exec(statement)
    requirement = result.one_or_none()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Cargar los artículos relacionados
    statement = select(Article).where(Article.requirement_id == requirement_id)
    articles = session.exec(statement).all()
    
    return {
        "id": requirement.id,
        "project_id": requirement.project_id,
        "request_date": requirement.request_date,
        "requested_by": requirement.requested_by,
        "state_id": requirement.state_id,
        "closing_date": requirement.closing_date,
        "articles": articles
    }
    
@router.delete("/{requirement_id}")
def delete_requirement(requirement_id: int, session: Session = Depends(get_session)):
    statement = delete(Requirement).where(Requirement.id == requirement_id)
    session.exec(statement)
    session.commit()
    return {"message": "Requirement deleted"}

@router.post("/", response_model=RequirementResponse)
def create_requirement(requirement: RequirementCreate, session: Session = Depends(get_session)):
    # Verify that the referenced entities exist
    if requirement.project_id:
        project = session.get(Project, requirement.project_id)
        if not project:
            raise HTTPException(status_code=400, detail="Invalid project_id")
    
    if requirement.requested_by:
        user = session.get(User, requirement.requested_by)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid requested_by")
    
    state = session.get(RequirementState, requirement.state_id)
    if not state:
        raise HTTPException(status_code=400, detail="Invalid state_id")
    
    db_requirement = Requirement.model_validate(requirement)
    session.add(db_requirement)
    session.commit()
    session.refresh(db_requirement)
    return {
        "id": db_requirement.id,
        "project_id": db_requirement.project_id,
        "request_date": db_requirement.request_date,
        "requested_by": db_requirement.requested_by,
        "state_id": db_requirement.state_id,
        "closing_date": db_requirement.closing_date,
        "articles": []
    }

@router.post("/with-articles", response_model=RequirementResponse)
def create_requirement_with_articles(
    data: RequirementWithArticlesCreate,
    session: Session = Depends(get_session)
):
    """Create a requirement with its associated articles"""
    # Verify that the referenced entities exist for the requirement
    if data.requirement.project_id:
        project = session.get(Project, data.requirement.project_id)
        if not project:
            raise HTTPException(status_code=400, detail="Invalid project_id")
    
    if data.requirement.requested_by:
        user = session.get(User, data.requirement.requested_by)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid requested_by")
    
    state = session.get(RequirementState, data.requirement.state_id)
    if not state:
        raise HTTPException(status_code=400, detail="Invalid state_id")

    # Create the requirement
    db_requirement = Requirement.model_validate(data.requirement)
    session.add(db_requirement)
    session.commit()
    session.refresh(db_requirement)

    # Create the articles
    created_articles = []
    for article_data in data.articles:
        # Verify that the referenced entities exist for each article
        if article_data.state_id:
            article_state = session.get(ArticleState, article_data.state_id)
            if not article_state:
                raise HTTPException(status_code=400, detail="Invalid article state_id")
        
        # Create the article with the requirement_id
        db_article = Article(
            requirement_id=db_requirement.id,
            quantity=article_data.quantity,
            unit=article_data.unit,
            brand=article_data.brand,
            model=article_data.model,
            dimensions=article_data.dimensions,
            state_id=article_data.state_id,
            notes=article_data.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(db_article)
        created_articles.append(db_article)
    
    session.commit()
    session.refresh(db_requirement)
    
    return {
        "id": db_requirement.id,
        "project_id": db_requirement.project_id,
        "request_date": db_requirement.request_date,
        "requested_by": db_requirement.requested_by,
        "state_id": db_requirement.state_id,
        "closing_date": db_requirement.closing_date,
        "articles": created_articles
    } 
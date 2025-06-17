from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import (
    Article, ArticleCreate, ArticleResponse, ArticleUpdate,
    Requirement, ArticleState
)
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=list[ArticleResponse])
def get_articles(session: Session = Depends(get_session)):
    statement = select(Article)
    results = session.exec(statement)
    return [{
        "id": article.id,
        "requirement_id": article.requirement_id,
        "requirement_consecutive": article.requirement_consecutive,
        "quantity": article.quantity,
        "unit": article.unit,
        "brand": article.brand,
        "model": article.model,
        "dimensions": article.dimensions,
        "state_id": article.state_id,
        "notes": article.notes
    } for article in results]
    
@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, session: Session = Depends(get_session)):
    statement = select(Article).where(Article.id == article_id)
    result = session.exec(statement)
    article = result.one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {
        "id": article.id,
        "requirement_id": article.requirement_id,
        "requirement_consecutive": article.requirement_consecutive,
        "quantity": article.quantity,
        "unit": article.unit,
        "brand": article.brand,
        "model": article.model,
        "dimensions": article.dimensions,
        "state_id": article.state_id,
        "notes": article.notes
    }

@router.post("/", response_model=ArticleResponse)
def create_article(article: ArticleCreate, session: Session = Depends(get_session)):
    # Verify that the referenced entities exist
    if article.requirement_id:
        requirement = session.get(Requirement, article.requirement_id)
        if not requirement:
            raise HTTPException(status_code=400, detail="Invalid requirement_id")
    
    if article.state_id:
        state = session.get(ArticleState, article.state_id)
        if not state:
            raise HTTPException(status_code=400, detail="Invalid state_id")
    
    db_article = Article.model_validate(article)
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return {
        "id": db_article.id,
        "requirement_id": db_article.requirement_id,
        "requirement_consecutive": db_article.requirement_consecutive,
        "quantity": db_article.quantity,
        "unit": db_article.unit,
        "brand": db_article.brand,
        "model": db_article.model,
        "dimensions": db_article.dimensions,
        "state_id": db_article.state_id,
        "notes": db_article.notes
    }

@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(article_id: int, article_update: ArticleUpdate, session: Session = Depends(get_session)):
    # Get the existing article
    statement = select(Article).where(Article.id == article_id)
    result = session.exec(statement)
    article = result.one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Verify that the referenced entities exist if they are being updated
    if article_update.requirement_id is not None:
        requirement = session.get(Requirement, article_update.requirement_id)
        if not requirement:
            raise HTTPException(status_code=400, detail="Invalid requirement_id")
    
    if article_update.state_id is not None:
        state = session.get(ArticleState, article_update.state_id)
        if not state:
            raise HTTPException(status_code=400, detail="Invalid state_id")
    
    # Update the article with the provided fields
    article_data = article_update.model_dump(exclude_unset=True)
    for key, value in article_data.items():
        if key == "quantity" and value is not None:
            setattr(article, key, Decimal(str(value)))
        else:
            setattr(article, key, value)
    
    # Update the updated_at timestamp
    article.updated_at = datetime.utcnow()
    
    session.add(article)
    session.commit()
    session.refresh(article)

    print(article.quantity)
    
    return {
        "id": article.id,
        "requirement_id": article.requirement_id,
        "requirement_consecutive": article.requirement_consecutive,
        "quantity": article.quantity,
        "unit": article.unit,
        "brand": article.brand,
        "model": article.model,
        "dimensions": article.dimensions,
        "state_id": article.state_id,
        "notes": article.notes
    }

@router.delete("/{article_id}")
def delete_article(article_id: int, session: Session = Depends(get_session)):
    statement = delete(Article).where(Article.id == article_id)
    session.exec(statement)
    session.commit()
    return {"message": "Article deleted"} 
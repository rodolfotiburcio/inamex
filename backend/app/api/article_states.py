from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.core.database import get_session
from app.models import ArticleState, ArticleStateCreate, ArticleStateResponse, Article, ArticleStateUpdate
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[ArticleStateResponse])
def get_article_states(session: Session = Depends(get_session)):
    statement = select(ArticleState)
    results = session.exec(statement)
    return [{
        "id": state.id,
        "name": state.name,
        "description": state.description,
        "order": state.order,
        "active": state.active,
        "created_at": state.created_at,
        "updated_at": state.updated_at
    } for state in results]
    
@router.get("/{state_id}", response_model=ArticleStateResponse)
def get_article_state(state_id: int, session: Session = Depends(get_session)):
    statement = select(ArticleState).where(ArticleState.id == state_id)
    result = session.exec(statement)
    state = result.one_or_none()
    if not state:
        raise HTTPException(status_code=404, detail="Article state not found")
    return {
        "id": state.id,
        "name": state.name,
        "description": state.description,
        "order": state.order,
        "active": state.active,
        "created_at": state.created_at,
        "updated_at": state.updated_at
    }

@router.post("/", response_model=ArticleStateResponse)
def create_article_state(state: ArticleStateCreate, session: Session = Depends(get_session)):
    db_state = ArticleState.model_validate(state)
    session.add(db_state)
    session.commit()
    session.refresh(db_state)
    return {
        "id": db_state.id,
        "name": db_state.name,
        "description": db_state.description,
        "order": db_state.order,
        "active": db_state.active,
        "created_at": db_state.created_at,
        "updated_at": db_state.updated_at
    }

@router.delete("/{state_id}")
def delete_article_state(state_id: int, session: Session = Depends(get_session)):
    # Check if state exists
    state = session.get(ArticleState, state_id)
    if not state:
        raise HTTPException(status_code=404, detail="Article state not found")
        
    # Check if state is being used
    statement = select(Article).where(Article.state_id == state_id)
    result = session.exec(statement)
    if result.first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete article state that is being used by articles"
        )
        
    session.delete(state)
    session.commit()
    return {"message": "Article state deleted"}

@router.put("/{state_id}", response_model=ArticleStateResponse)
def update_article_state(
    state_id: int, 
    state_data: ArticleStateUpdate, 
    session: Session = Depends(get_session)
):
    # Get existing state
    statement = select(ArticleState).where(ArticleState.id == state_id)
    result = session.exec(statement)
    db_state = result.one_or_none()
    
    if not db_state:
        raise HTTPException(status_code=404, detail="Article state not found")
    
    # Update the state with new data (only provided fields)
    state_dict = state_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in state_dict.items():
        setattr(db_state, key, value)
    
    db_state.updated_at = datetime.utcnow()
    session.add(db_state)
    session.commit()
    session.refresh(db_state)
    
    return {
        "id": db_state.id,
        "name": db_state.name,
        "description": db_state.description,
        "order": db_state.order,
        "active": db_state.active,
        "created_at": db_state.created_at,
        "updated_at": db_state.updated_at
    } 
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, delete
from app.models import User, UserCreate, UserResponse, UserUpdate
from app.core.database import get_session
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[UserResponse])
def get_users(session: Session = Depends(get_session)):
    statement = select(User)
    results = session.exec(statement)
    users = [{
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "password_hash": user.password_hash
    } for user in results]
    return users
    
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "password_hash": user.password_hash
    }
    
@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    statement = delete(User).where(User.id == user_id)
    session.exec(statement)
    session.commit()
    return {"message": "User deleted"}

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Verificar si el nombre de usuario ya existe
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {
        "id": db_user.id,
        "username": db_user.username,
        "full_name": db_user.full_name,
        "password_hash": db_user.password_hash
    }

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)):
    # Obtener el usuario existente
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    db_user = result.one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Si se actualiza el nombre de usuario, verificar que no exista
    if user_data.username is not None and user_data.username != db_user.username:
        username_check = select(User).where(User.username == user_data.username)
        existing_user = session.exec(username_check).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Actualizar los campos proporcionados
    user_data_dict = user_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in user_data_dict.items():
        setattr(db_user, key, value)
    
    # Actualizar la fecha de modificación
    from datetime import datetime
    db_user.updated_at = datetime.utcnow()
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "full_name": db_user.full_name,
        "password_hash": db_user.password_hash
    } 
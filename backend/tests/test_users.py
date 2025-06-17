from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.core.database import engine
from sqlmodel import Session, select

client = TestClient(app)

def test_create_user():
    """Test creating a new user"""
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "full_name": "Test User",
            "password_hash": "hashedpassword123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "password_hash" in data

    # Clean up
    with Session(engine) as session:
        statement = select(User).where(User.username == "testuser")
        test_user = session.exec(statement).first()
        if test_user:
            session.delete(test_user)
            session.commit()

def test_create_user_duplicate_username():
    """Test that creating a user with duplicate username fails"""
    # Crear un usuario primero
    user = User(username="existinguser", full_name="Existing User", password_hash="password123")
    with Session(engine) as session:
        session.add(user)
        session.commit()
    
    # Intentar crear otro con el mismo username
    response = client.post(
        "/users/",
        json={
            "username": "existinguser",
            "full_name": "Another User",
            "password_hash": "anotherpassword"
        },
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

    # Clean up
    with Session(engine) as session:
        statement = select(User).where(User.username == "existinguser")
        test_user = session.exec(statement).first()
        if test_user:
            session.delete(test_user)
            session.commit()

def test_get_users():
    """Test getting all users"""
    # Crear algunos usuarios de prueba
    user1 = User(username="user1", full_name="User One", password_hash="pass1")
    user2 = User(username="user2", full_name="User Two", password_hash="pass2")
    with Session(engine) as session:
        session.add(user1)
        session.add(user2)
        session.commit()
    
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    usernames = [user["username"] for user in data]
    assert "user1" in usernames
    assert "user2" in usernames

    # Clean up
    with Session(engine) as session:
        statement = select(User).where(User.username.in_(["user1", "user2"]))
        test_users = session.exec(statement).all()
        for user in test_users:
            session.delete(user)
        session.commit()

def test_get_user():
    """Test getting a specific user by ID"""
    # Crear usuario de prueba
    user = User(username="getuser", full_name="Get User", password_hash="getpass")
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "getuser"
    assert data["full_name"] == "Get User"

    # Clean up
    with Session(engine) as session:
        test_user = session.get(User, user_id)
        if test_user:
            session.delete(test_user)
            session.commit()

def test_get_user_not_found():
    """Test getting a non-existent user"""
    response = client.get("/users/999999")  # ID que seguramente no existe
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_update_user():
    """Test updating a user"""
    # Crear usuario de prueba
    user = User(username="updateuser", full_name="Original Name", password_hash="originalpass")
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    
    # Actualizar solo el nombre completo
    response = client.put(
        f"/users/{user_id}",
        json={
            "full_name": "Updated Name"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "updateuser"  # No cambió
    assert data["full_name"] == "Updated Name"  # Cambió
    
    # Verificar que se actualizó en la base de datos
    with Session(engine) as session:
        updated_user = session.get(User, user_id)
        assert updated_user.full_name == "Updated Name"
        assert updated_user.username == "updateuser"
        
        # Cleanup
        session.delete(updated_user)
        session.commit()

def test_update_user_username():
    """Test updating a user's username"""
    # Crear usuario de prueba
    user = User(username="oldusername", full_name="Some User", password_hash="somepass")
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    
    # Actualizar el nombre de usuario
    response = client.put(
        f"/users/{user_id}",
        json={
            "username": "newusername"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newusername"
    
    # Verificar que se actualizó en la base de datos
    with Session(engine) as session:
        updated_user = session.get(User, user_id)
        assert updated_user.username == "newusername"
        
        # Cleanup
        session.delete(updated_user)
        session.commit()

def test_update_user_duplicate_username():
    """Test that updating a user with an existing username fails"""
    # Crear dos usuarios
    user1 = User(username="user1dup", full_name="User One", password_hash="pass1")
    user2 = User(username="user2dup", full_name="User Two", password_hash="pass2")
    with Session(engine) as session:
        session.add(user1)
        session.add(user2)
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        user1_id = user1.id
        user2_id = user2.id
    
    # Intentar actualizar user2 con el username de user1
    response = client.put(
        f"/users/{user2_id}",
        json={
            "username": "user1dup"
        }
    )
    
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]
    
    # Verificar que no cambió
    with Session(engine) as session:
        updated_user = session.get(User, user2_id)
        assert updated_user.username == "user2dup"
        
        # Cleanup
        session.delete(session.get(User, user1_id))
        session.delete(updated_user)
        session.commit()

def test_update_user_not_found():
    """Test updating a non-existent user"""
    response = client.put(
        "/users/999999",  # ID que seguramente no existe
        json={
            "full_name": "Won't Update"
        }
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_delete_user():
    """Test deleting a user"""
    # Crear usuario de prueba
    user = User(username="deleteuser", full_name="Delete User", password_hash="deletepass")
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    
    # Eliminar el usuario
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    
    # Verificar que el usuario fue eliminado
    with Session(engine) as session:
        deleted_user = session.get(User, user_id)
        assert deleted_user is None 
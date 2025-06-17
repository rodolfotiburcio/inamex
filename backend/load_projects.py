import json
from sqlmodel import Session, select
from app.core.database import engine
from app.models import Project, ProjectState, User, Client
from datetime import datetime
import hashlib
import re

def clean_username(name):
    # Limpiar el nombre de espacios en blanco y caracteres especiales
    name = name.strip()
    # Reemplazar múltiples espacios por un solo guión bajo
    name = re.sub(r'\s+', '_', name)
    # Convertir a minúsculas
    return name.lower()

def load_projects():
    # Leer el archivo JSON
    with open('dev/old-data/projects.json', 'r') as f:
        projects_data = json.load(f)
    
    # Crear una sesión de base de datos
    with Session(engine) as session:
        # Contadores para estadísticas
        total_projects = len(projects_data)
        created_projects = 0
        skipped_projects = 0
        
        # Diccionarios para mapear nombres a IDs
        project_states = {}  # nombre -> id
        users = {}  # nombre -> id
        clients = {}  # id_antiguo -> id_nuevo
        
        # Obtener todos los clientes existentes
        statement = select(Client)
        existing_clients = session.exec(statement).all()
        for client in existing_clients:
            # Buscar el ID antiguo en el nombre (si está en el formato "nombre (id)")
            if "(" in client.name and ")" in client.name:
                try:
                    old_id = int(client.name.split("(")[1].split(")")[0])
                    clients[old_id] = client.id
                except ValueError:
                    # Ignorar el caso especial de "Desconocido (\\N)"
                    if "\\N" in client.name:
                        # Asignar el ID 21 que corresponde a "Desconocido (\\N)"
                        clients[21] = client.id
                    continue
        
        # Obtener todos los usuarios existentes
        statement = select(User)
        existing_users = session.exec(statement).all()
        for user in existing_users:
            users[user.username] = user.id
        
        # Primera pasada: crear estados de proyecto y usuarios únicos
        for project in projects_data:
            # Crear estado de proyecto si no existe
            if project['status'] not in project_states:
                state = ProjectState(
                    name=project['status'],
                    description=f"Estado de proyecto: {project['status']}",
                    order=0,
                    active=True
                )
                session.add(state)
                session.commit()
                session.refresh(state)
                project_states[project['status']] = state.id
            
            # Crear usuario si no existe
            if project['manager'] and project['manager'].strip():
                manager_name = project['manager'].strip()
                username = clean_username(manager_name)
                
                # Verificar si el usuario ya existe
                if username not in users:
                    # Generar un hash de contraseña simple
                    password_hash = hashlib.sha256("password123".encode()).hexdigest()
                    
                    user = User(
                        username=username,
                        full_name=manager_name,
                        password_hash=password_hash
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    users[username] = user.id
        
        # Segunda pasada: crear proyectos
        for project in projects_data:
            # Verificar si el proyecto ya existe por su número
            statement = select(Project).where(Project.number == project['ccinx'])
            existing_project = session.exec(statement).first()
            if existing_project:
                print(f"Skipping existing project: {project['ccinx']}")
                skipped_projects += 1
                continue
            
            # Obtener el ID del cliente
            client_id = None
            if project['client_id'] is not None:
                client_id = clients.get(project['client_id'])
                if client_id is None:
                    print(f"Warning: No se encontró el cliente con ID antiguo {project['client_id']}")
                    continue
            
            # Obtener el ID del responsable
            responsible_id = None
            if project['manager'] and project['manager'].strip():
                username = clean_username(project['manager'].strip())
                responsible_id = users.get(username)
            
            # Crear el proyecto
            new_project = Project(
                number=project['ccinx'],
                name=project['name'],
                date=datetime.strptime(project['start_date'], '%Y-%m-%d') if project['start_date'] else datetime.utcnow(),
                state_id=project_states[project['status']],
                responsible_id=responsible_id,
                client_id=client_id
            )
            session.add(new_project)
            created_projects += 1
        
        # Guardar los cambios
        session.commit()
        
        # Mostrar estadísticas
        print(f"\nResumen de la carga:")
        print(f"Total de proyectos en el archivo: {total_projects}")
        print(f"Proyectos creados: {created_projects}")
        print(f"Proyectos existentes (omitidos): {skipped_projects}")
        print(f"Estados de proyecto creados: {len(project_states)}")
        print(f"Usuarios existentes: {len(users)}")

if __name__ == "__main__":
    load_projects() 
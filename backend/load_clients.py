import json
from sqlmodel import Session, select
from app.core.database import engine
from app.models import Client

def load_clients():
    # Leer el archivo JSON
    try:
        with open('dev/old-data/clients.json', 'r') as f:
            content = f.read()
            print("Contenido del archivo:")
            print(content[:1000])  # Imprimir los primeros 1000 caracteres
            clients_data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        print(f"Posición del error: {e.pos}")
        print(f"Línea: {e.lineno}, Columna: {e.colno}")
        return
    except Exception as e:
        print(f"Error inesperado: {e}")
        return
    
    # Crear una sesión de base de datos
    with Session(engine) as session:
        # Verificar si ya existen clientes
        statement = select(Client)
        existing_clients = session.exec(statement).all()
        existing_names = {client.name for client in existing_clients}
        
        # Contadores para estadísticas
        total = len(clients_data)
        created = 0
        skipped = 0
        
        # Procesar cada cliente
        for client_data in clients_data:
            # Crear el nombre incluyendo el ID antiguo
            name = f"{client_data['name']} ({client_data['id']})"
            
            # Saltar si el cliente ya existe
            if name in existing_names:
                print(f"Skipping existing client: {name}")
                skipped += 1
                continue
            
            # Crear el cliente
            client = Client(name=name)
            session.add(client)
            created += 1
        
        # Guardar los cambios
        session.commit()
        
        # Mostrar estadísticas
        print(f"\nResumen de la carga:")
        print(f"Total de clientes en el archivo: {total}")
        print(f"Clientes creados: {created}")
        print(f"Clientes existentes (omitidos): {skipped}")

if __name__ == "__main__":
    load_clients() 
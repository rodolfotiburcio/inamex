## Orden para implementar modelos
1. Definir el modelo en database.dbml
2. Crear el archivo en /app/models/
3. Se agrega el modelo a /app/models/__init__.py
4. Se crean los endpoint de la api en /app/api/{model_name}.py
5. Se agregan los nuevos endpoints a /app/api/__init__.py
6. Se crean los test para el nuevo endpoint en /tests/test_{model_name}.py
    - Los test no usan fixtures, se crean los datos necesarios en cada test

### Notas importantes
- Se usa SQLModel para definir los modelos, los endpoints y los test.
- No se usa alembic para las migraciones, se usa SQLModel para crear las tablas en la base de datos.
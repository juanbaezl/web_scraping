import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from alembic import context

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.settings.database import Base

from app import models  # importa todos los modelos para que Alembic los reconozca

# Archivo de configuración de Alembic, alembic.ini
config = context.config

# Obtener la URL de la base de datos desde la variable de entorno
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/openlibrary"
if not DB_USER or not DB_PASSWORD or not DB_HOST or not DB_PORT:
    raise ValueError(
        "Las variables de entorno de la base de datos no están configuradas."
    )
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Verificar si hay un archivo de configuración
if config.config_file_name is not None:
    # Configurar el logging desde el archivo de configuración
    fileConfig(config.config_file_name)

# Apuntar a la metadata de los modelos
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'.

    En este escenario no necesitamos una conexión a la base de datos.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecutar migraciones en modo 'online'.

    En este escenario necesitamos crear un Engine
    y asociar una conexión con el contexto.
    """
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Determinar si estamos en modo offline o online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

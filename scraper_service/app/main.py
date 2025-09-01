from fastapi import FastAPI

# Importaciones locales
from app.settings.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

# --- Instancia de la Aplicación FastAPI ---
app = FastAPI(
    title="Open Library Scraper API",
    description="Una API para extraer y consultar datos de libros de Open Library.",
    version="1.0.0",
)


# --- Inyección de Dependencias para la Sesión de la DB ---
def get_db():
    """
    Esta función genera una sesión de base de datos por cada petición
    y se asegura de cerrarla al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoints de la API ---


@app.get("/")
def read_root():
    """Endpoint raíz para verificar que la API está en funcionamiento."""
    return {"status": "API en funcionamiento"}

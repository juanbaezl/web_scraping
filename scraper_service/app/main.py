from fastapi import FastAPI
from fastapi.params import Depends
from requests import Session

# Importaciones locales
from app.models.subject import Subject
from app.settings.database import SessionLocal, engine, Base
from app.tasks.book import BookScraper
from app.tasks.subject import SubjectScraper

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


@app.get("/scrape/subjects")
def scrape_subjects(db: Session = Depends(get_db)):
    """Endpoint para obtener todos los géneros disponibles."""
    subject_task = SubjectScraper(db)
    subject_task.scrape_and_store_subjects()
    return {"status": "Géneros extraídos y almacenados correctamente"}


@app.get("/scrape/books/{book_id}")
def scrape_book(book_id: int, db: Session = Depends(get_db)):
    """Endpoint para extraer información de un libro específico."""
    book_service = BookScraper(db)
    book_info = book_service.scrape_single_book(book_id, create_in_db=False)
    if book_info:
        return {"status": "Libro extraído correctamente", "data": book_info}
    return {"status": "Error al extraer el libro"}


@app.get("/scrape/books")
def scrape_books(
    start_id: int,
    end_id: int,
    batch_size: int,
    num_threads: int,
    db: Session = Depends(get_db),
):
    """Endpoint para extraer información de múltiples libros."""
    book_service = BookScraper(db)
    book_service.scrape_and_store_books_by_id_range(
        start_id, end_id, batch_size, num_threads
    )
    return {"status": "Libros extraídos y almacenados correctamente"}

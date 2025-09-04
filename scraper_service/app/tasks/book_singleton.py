from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import logging

# Importa todos los modelos necesarios
from app.models import Book


class BookSingleton:
    """
    Clase para extraer y almacenar información de libros desde Open Library.
    """

    def __init__(self):
        logging.info("BookSingleton iniciado")

    def create_book(self, book_data: dict, db: Session):
        """
        Crea un libro en la base de datos si no existe.

        Args:
            book_data (dict): Datos del libro a crear.
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.

        Returns:
            Book: El libro creado o existente.
        """
        book_id = book_data.get("open_library_id")
        if not book_id:
            return None
        book = (
            db.query(Book)
            .filter(Book.open_library_id == book_data["open_library_id"])
            .first()
        )
        if not book:
            with db.begin_nested() as savepoint:
                try:
                    book = Book(
                        open_library_id=book_data["open_library_id"],
                        work_id=book_data["work_id"],
                        title=book_data["title"],
                        publish_year=book_data["publish_year"],
                        pages=book_data["pages"],
                        language=book_data["language"],
                        publisher=book_data["publisher"],
                        authors=list(book_data["authors"]),
                        subjects=list(book_data["subjects"]),
                        rating=book_data["rating"],
                        rating_count=book_data["rating_count"],
                        want_to_read_count=book_data["want_to_read_count"],
                        read_count=book_data["read_count"],
                        currently_reading_count=book_data["currently_reading_count"],
                    )
                    db.add(book)
                    db.flush()
                    return book
                except (IntegrityError, UniqueViolation) as e:
                    savepoint.rollback()

    def bulk_create_books(self, books_data: list[dict], db: Session):
        """
        Crea múltiples libros en la base de datos.

        Args:
            books_data (list[dict]): Lista de datos de libros a crear.
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        """
        ids = [b["open_library_id"] for b in books_data]
        existing_books = db.query(Book).filter(Book.open_library_id.in_(ids)).all()
        existing_book_ids = {book.open_library_id for book in existing_books}
        new_books = [
            book
            for book in books_data
            if book["open_library_id"] not in existing_book_ids
        ]
        if new_books:
            with db.begin_nested() as savepoint:
                try:
                    db.bulk_insert_mappings(Book, new_books)
                    db.flush()
                except (IntegrityError, UniqueViolation):
                    savepoint.rollback()
        return db.query(Book).filter(Book.open_library_id.in_(ids)).all()


book_singleton = BookSingleton()

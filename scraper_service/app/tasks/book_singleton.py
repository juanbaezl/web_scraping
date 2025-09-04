from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Importa todos los modelos necesarios
from app.models import Book


class BookSingleton:
    """
    Clase para extraer y almacenar información de libros desde Open Library.
    """

    def __init__(self):
        print("BookSingleton iniciado")

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
                    author = Book(
                        open_library_id=book_data["open_library_id"],
                        work_id=book_data["working_id"],
                        title=book_data["title"],
                        publish_year=book_data["publish_date"],
                        pages=book_data["pages"],
                        language=book_data["language"],
                        publisher=book_data["publisher"],
                        authors=list(book_data["authors"]),
                        subjects=list(book_data["subjects"]),
                        rating=book_data["rating_value"],
                        rating_count=book_data["rating_count"],
                        want_to_read_count=book_data["want_to_read_count"],
                        read_count=book_data["read_count"],
                        currently_reading_count=book_data["currently_reading_count"],
                    )
                    db.add(author)
                    db.flush()
                    return author
                except (IntegrityError, UniqueViolation) as e:
                    savepoint.rollback()


book_singleton = BookSingleton()

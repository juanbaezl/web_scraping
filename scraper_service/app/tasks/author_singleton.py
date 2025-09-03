from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Importa todos los modelos necesarios
from app.models import Author

from functools import lru_cache


class AuthorSingleton:
    """
    Clase para extraer y almacenar información de autores desde Open Library.
    """

    def __init__(self):
        print("AuthorSingleton iniciado")

    @lru_cache(maxsize=128)
    def get_or_create_author(self, author_name: str, db: Session) -> Author:
        """
        Obtiene un autor de la base de datos o lo crea si no existe.
        Args:
            author_name (str): El nombre del autor.
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        Returns:
            Author: El autor obtenido o creado.
        """
        author = db.query(Author).filter(Author.name == author_name).first()
        if not author:
            try:
                author = Author(name=author_name)
                db.add(author)
                db.flush()
                return author
            except (IntegrityError, UniqueViolation) as e:
                db.rollback()
                author = db.query(Author).filter(Author.name == author_name).one()
                return author

        return author


author_singleton = AuthorSingleton()

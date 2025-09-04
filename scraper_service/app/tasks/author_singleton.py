from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import logging

# Importa todos los modelos necesarios
from app.models import Author

from functools import lru_cache


class AuthorSingleton:
    """
    Clase para extraer y almacenar información de autores desde Open Library.
    """

    def __init__(self):
        logging.info("AuthorSingleton iniciado")

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
            with db.begin_nested() as savepoint:
                try:
                    author = Author(name=author_name)
                    db.add(author)
                    db.flush()
                    return author
                except (IntegrityError, UniqueViolation) as e:
                    savepoint.rollback()
                    author = db.query(Author).filter(Author.name == author_name).one()
                    return author

        return author

    def bulk_get_or_create_author(
        self, authors: list[str], db: Session
    ) -> list[Author]:
        """
        Obtiene o crea múltiples autores en la base de datos.
        Args:
            authors (list[str]): Lista de nombres de autores.
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        Returns:
            list[Author]: Lista de autores obtenidos o creados.
        """
        existing_authors = db.query(Author).filter(Author.name.in_(authors)).all()
        existing_author_names = {author.name for author in existing_authors}
        new_authors = [
            {"name": name} for name in authors if name not in existing_author_names
        ]
        if new_authors:
            with db.begin_nested() as savepoint:
                try:
                    db.bulk_insert_mappings(Author, new_authors)
                    db.flush()
                except (IntegrityError, UniqueViolation) as e:
                    savepoint.rollback()
        return db.query(Author).filter(Author.name.in_(authors)).all()


author_singleton = AuthorSingleton()

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    Text,
    Float,
)

from sqlalchemy.orm import relationship

from app.settings.database import Base

book_subjects_association = Table(
    "book_subjects",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id"), primary_key=True),
)

book_authors_association = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class Book(Base):
    """Modelo que representa un libro en la base de datos.

    Args:
        Base : Hereda de la base declarativa de SQLAlchemy.
    """

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    open_library_id = Column(String, unique=True, index=True)
    work_id = Column(String, nullable=True)
    title = Column(String, index=True)
    publish_year = Column(Integer, nullable=True)
    pages = Column(Integer, nullable=True)
    language = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    # Relación muchos a muchos: Muchos libros pueden tener muchos autores.
    authors = relationship(
        "Author", secondary=book_authors_association, backref="books"
    )

    # Relación muchos a muchos: Un libro puede tener muchos géneros y viceversa.
    subjects = relationship(
        "Subject", secondary=book_subjects_association, backref="books"
    )

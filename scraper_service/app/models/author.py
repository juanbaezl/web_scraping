from sqlalchemy import (
    Column,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.settings.database import Base


class Author(Base):
    """Modelo que representa a un autor en la base de datos.

    Args:
        Base: Hereda de la base declarativa de SQLAlchemy.
    """

    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relación uno a muchos: Un autor puede tener muchos libros.
    books = relationship("Book", back_populates="author")

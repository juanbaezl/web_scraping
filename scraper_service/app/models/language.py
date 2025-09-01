from sqlalchemy import (
    Column,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.settings.database import Base


class Language(Base):
    """Modelo que representa un idioma en la base de datos.

    Args:
        Base: Hereda de la base declarativa de SQLAlchemy.
    """

    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relación uno a muchos: Un idioma puede tener muchos libros.
    books = relationship("Book", back_populates="language")

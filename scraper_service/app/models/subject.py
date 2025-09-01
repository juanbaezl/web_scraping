from sqlalchemy import (
    Column,
    Integer,
    String,
)


from app.settings.database import Base


class Subject(Base):
    """Modelo que representa un genero en la base de datos.

    Args:
        Base: Hereda de la base declarativa de SQLAlchemy.
    """

    __tablename__ = "subjects"

    # Lo mismo aquí, ID auto-generado por defecto.
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

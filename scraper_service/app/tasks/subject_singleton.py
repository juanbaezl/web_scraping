from functools import lru_cache
from sqlalchemy.orm import Session

from app.models.subject import Subject


class SubjectSingleton:
    """
    Clase para manejar la creación y obtención de géneros de manera eficiente.
    """

    def __init__(self):
        print("SubjectSingleton iniciado")

    @lru_cache(maxsize=64)
    def get_subject(self, subject_name: str, db: Session) -> Subject:
        """
        Obtiene un género de la base de datos o lo crea si no existe.
        Args:
            subject_name (str): El nombre del género.
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        Returns:
            Subject: El género obtenido o creado.
        """
        subject = db.query(Subject).filter(Subject.name == subject_name).first()
        return subject


subject_singleton = SubjectSingleton()

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.utils.constants import BASE_URL, HEADERS, SUBJECTS_QUERY
from app.models.subject import Subject


class SubjectScraper:
    """Clase para extraer y almacenar géneros de libros desde Open Library.

    Args:
        db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.

    Métodos:
        scrape_and_store_subjects: Extrae los géneros y los almacena en la base de datos.
    """

    def __init__(self, db: Session):
        """Inicializa el scraper de géneros.

        Args:
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        """
        self.db = db

    def scrape_and_store_subjects(self):
        """Extrae los géneros de la página de Open Library y los almacena en la base de datos."""
        response = requests.get(f"{BASE_URL}/subjects", headers=HEADERS, timeout=20)
        if response.status_code != 200:
            raise Exception(f"Error al acceder a {BASE_URL}: {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        subject_elements = soup.select(SUBJECTS_QUERY)
        unique_subjects = set()
        for element in subject_elements:
            subject_name = element.get_text(strip=True)
            if subject_name:
                # Verificar si el género ya existe en la base de datos
                existing_subject = (
                    self.db.query(Subject).filter(Subject.name == subject_name).first()
                )
                if not existing_subject and subject_name not in unique_subjects:
                    new_subject = Subject(name=subject_name)
                    self.db.add(new_subject)
                    unique_subjects.add(subject_name)

        self.db.commit()
        self.db.close()

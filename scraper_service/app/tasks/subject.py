import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.subject import Subject


class SubjectScraper:
    """Clase para extraer y almacenar géneros de libros desde Open Library.

    Args:
        db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.

    Métodos:
        scrape_and_store_subjects: Extrae los géneros y los almacena en la base de datos.
    """

    BASE_URL = "https://openlibrary.org/subjects"

    def __init__(self, db: Session):
        """Inicializa el scraper de géneros.

        Args:
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        """
        self.db = db

    def scrape_and_store_subjects(self):
        """Extrae los géneros de la página de Open Library y los almacena en la base de datos."""
        headers = {"Accept-Language": "es"}
        response = requests.get(self.BASE_URL, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Error al acceder a {self.BASE_URL}: {response.status_code}"
            )

        soup = BeautifulSoup(response.content, "html.parser")
        subject_elements = soup.select("div#subjectsPage li a:not([href*='language'])")
        for element in subject_elements:
            subject_name = element.get_text(strip=True)
            # if subject_name:
            # Verificar si el género ya existe en la base de datos
            # existing_subject = (
        #             self.db.query(Subject).filter(Subject.name == subject_name).first()
        #         )
        #         if not existing_subject:
        #             new_subject = Subject(name=subject_name)
        #             self.db.add(new_subject)

        # self.db.commit()
        # self.db.close()

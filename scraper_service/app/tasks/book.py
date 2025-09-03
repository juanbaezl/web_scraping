import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.utils.constants import (
    BASE_URL,
    BOOKS_LANGUAGE_QUERY,
    HEADERS,
    BOOKS_NAME_QUERY,
    BOOKS_AUTHOR_QUERY,
    BOOKS_SUBJECT_QUERY,
    BOOKS_ITEMS_QUERY,
    BOOKS_PUBLISH_DATE_QUERY,
    BOOKS_PUBLISHER_QUERY,
    BOOKS_PAGES_QUERY,
    BOOKS_CURRENTLY_READING_COUNT_QUERY,
    BOOKS_READ_COUNT_QUERY,
    BOOKS_WANT_TO_READ_COUNT_QUERY,
    BOOKS_STATS_QUERY,
    BOOKS_RATING_COUNT_QUERY,
    BOOKS_RATING_VALUE_QUERY,
    BOOKS_WORKING_ID_QUERY,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.tasks.author_singleton import author_singleton
from app.tasks.subject_singleton import subject_singleton

# Importa todos los modelos necesarios
from app.models import Book, Subject


class BookScraper:
    """
    Clase para extraer y almacenar información de libros desde Open Library.
    Args:
        db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
    """

    def __init__(self, db: Session):
        """
        Inicializa el servicio de libros.
        Args:
            db (Session): Una sesión de SQLAlchemy para interactuar con la base de datos.
        """
        self.db = db

    def scrape_single_book(self, book_id: int) -> dict:
        """
        Extrae la información de un solo libro dado su ID.
        Args:
            book_id (int): El ID del libro en Open Library.
        Returns:
            dict: Un diccionario con la información del libro.
        """
        url = f"{BASE_URL}/books/OL{book_id}M"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error al acceder a {url}: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        # Extrae el título
        title = soup.select_one(BOOKS_NAME_QUERY).get_text(strip=True)
        # Extrae los autores
        authors_scrap = soup.select(BOOKS_AUTHOR_QUERY)
        authors = set()
        for author in authors_scrap:
            author_name = author.get_text(strip=True)
            # author_db = author_singleton.get_or_create_author(author_name, self.db)
            authors.add(author_name)
        # Extrae los géneros
        subjects_scrap = soup.select(BOOKS_SUBJECT_QUERY)
        subjects = set()
        for subject in subjects_scrap:
            subject_name = subject.get_text(strip=True)
            subject_db = subject_singleton.get_subject(subject_name, self.db)
            subjects.add(subject_db.id) if subject_db else None
        # Extrae items generales
        general_items = soup.select_one(BOOKS_ITEMS_QUERY)
        language = None
        publish_date = None
        publisher = None
        if general_items:
            # Extrae el idioma
            language = general_items.select_one(BOOKS_LANGUAGE_QUERY)
            language = language.get_text(strip=True) if language else "Desconocido"
            # extrae la fecha de publicación
            publish_date = general_items.select_one(BOOKS_PUBLISH_DATE_QUERY)
            publish_date = (
                publish_date.get_text(strip=True) if publish_date else "Desconocido"
            )
            # extrae la editorial del libro
            publisher = general_items.select_one(BOOKS_PUBLISHER_QUERY)
            publisher = publisher.get_text(strip=True) if publisher else "Desconocido"
            # extrae las páginas del libro
            pages = general_items.select_one(BOOKS_PAGES_QUERY)
            pages = pages.get_text(strip=True) if pages else "Desconocido"

        stats = soup.select_one(BOOKS_STATS_QUERY)
        rating_value = None
        rating_count = None
        want_to_read_count = None
        read_count = None
        currently_reading_count = None
        if stats:
            # Extrae la valoración del libro
            rating_value = stats.select_one(BOOKS_RATING_VALUE_QUERY)
            rating_value = rating_value["content"] if rating_value else "0"
            # Extrae el número de valoraciones
            rating_count = stats.select_one(BOOKS_RATING_COUNT_QUERY)
            rating_count = rating_count["content"] if rating_count else "0"
            # Extrae el número de usuarios que quieren leer el libro
            want_to_read_count = soup.select_one(BOOKS_WANT_TO_READ_COUNT_QUERY)
            want_to_read_count = (
                want_to_read_count.get_text(strip=True) if want_to_read_count else "0"
            )
            # Extrae el número de usuarios que han leído el libro
            read_count = soup.select_one(BOOKS_READ_COUNT_QUERY)
            read_count = read_count.get_text(strip=True) if read_count else "0"
            # Extrae el número de usuarios que están leyendo el libro
            currently_reading_count = soup.select_one(
                BOOKS_CURRENTLY_READING_COUNT_QUERY
            )
            currently_reading_count = (
                currently_reading_count.get_text(strip=True)
                if currently_reading_count
                else "0"
            )
        # Extrae el ID del trabajo
        working_id = soup.select_one(BOOKS_WORKING_ID_QUERY)
        working_id = working_id.get_text(strip=True) if working_id else "Desconocido"

        return {
            "title": title,
            "authors": authors,
            "subjects": subjects,
            "language": language if language else None,
            "publish_date": publish_date if publish_date else None,
            "publisher": publisher if publisher else None,
            "pages": pages if pages else None,
            "rating_value": rating_value if rating_value else None,
            "rating_count": rating_count if rating_count else None,
            "want_to_read_count": want_to_read_count if want_to_read_count else None,
            "read_count": read_count if read_count else None,
            "currently_reading_count": (
                currently_reading_count if currently_reading_count else None
            ),
            "working_id": working_id if working_id else None,
        }

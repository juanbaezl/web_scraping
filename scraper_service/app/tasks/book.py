import logging
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
from app.tasks.book_singleton import book_singleton
from app.utils.numbers import get_integer, get_float

# Importa todos los modelos necesarios
from app.models import Book
from app.models.book import book_authors_association, book_subjects_association


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

    def _scrap_title(self, soup: BeautifulSoup) -> str:
        """Extrae el título del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            str: El título del libro.
        """
        title = soup.select_one(BOOKS_NAME_QUERY)
        return title.get_text(strip=True) if title else "Desconocido"

    def _scrap_authors(self, soup: BeautifulSoup) -> set:
        """
        Extrae los autores del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            set: Un conjunto de IDs de autores o nombres de autores.
        """
        authors_scrap = soup.select(BOOKS_AUTHOR_QUERY)
        authors = set()
        for author in authors_scrap:
            author_name = author.get_text(strip=True)
            authors.add(author_name)
        return authors if len(authors) > 0 else ["Desconocido"]

    def _scrap_subjects(self, soup: BeautifulSoup, create_in_db: bool = True) -> set:
        """
        Extrae los géneros del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            set: Un conjunto de IDs de géneros.
        """
        subjects_scrap = soup.select(BOOKS_SUBJECT_QUERY)
        subjects_scrap = subjects_scrap if subjects_scrap else ["Desconocido"]
        subjects = set()
        for subject in subjects_scrap:
            subject_name = (
                subject.get_text(strip=True)
                if not isinstance(subject, str)
                else subject
            )
            subject_db = subject_singleton.get_subject(subject_name, self.db)
            (
                subjects.add(subject_db)
                if subject_db
                else None if create_in_db else subjects.add(subject_name)
            )
        return subjects

    def _scrap_language(self, soup: BeautifulSoup) -> str:
        """
        Extrae el idioma del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            str: El idioma del libro.
        """
        language = soup.select_one(BOOKS_LANGUAGE_QUERY)
        return language.get_text(strip=True) if language else "Desconocido"

    def _scrap_publish_date(self, soup: BeautifulSoup) -> str:
        """
        Extrae la fecha de publicacion del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            str: la fecha de publicacion del libro.
        """
        publish_date = soup.select_one(BOOKS_PUBLISH_DATE_QUERY)
        return get_integer(publish_date.get_text(strip=True)) if publish_date else -1

    def _scrap_publisher(self, soup: BeautifulSoup) -> str:
        """
        Extrae la editorial del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            str: la editorial del libro.
        """
        publisher = soup.select_one(BOOKS_PUBLISHER_QUERY)
        return publisher.get_text(strip=True) if publisher else "Desconocido"

    def _scrap_pages(self, soup: BeautifulSoup) -> str:
        """
        Extrae el número de páginas del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            str: el número de páginas del libro.
        """
        pages = soup.select_one(BOOKS_PAGES_QUERY)
        return get_integer(pages.get_text(strip=True)) if pages else -1

    def _scrap_general_items(self, soup: BeautifulSoup) -> tuple:
        """
        Extrae los items generales del libro como el idioma, la fecha de publicación, la editorial y el número de páginas.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            tuple: Una tupla con el idioma, la fecha de publicación, la editorial y el número de páginas.
        """
        general_items = soup.select_one(BOOKS_ITEMS_QUERY)
        language = None
        publish_date = None
        publisher = None
        pages = None
        if general_items:
            language = self._scrap_language(general_items)
            publish_date = self._scrap_publish_date(general_items)
            publisher = self._scrap_publisher(general_items)
            pages = self._scrap_pages(general_items)
        return language, publish_date, publisher, pages

    def _scrap_rating_value(self, soup: BeautifulSoup) -> float:
        """
        Extrae la valoración del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            float: La valoración del libro.
        """
        rating_value = soup.select_one(BOOKS_RATING_VALUE_QUERY)
        return (
            get_float(rating_value["content"])
            if rating_value and "content" in rating_value.attrs
            else 0.0
        )

    def _scrap_rating_count(self, soup: BeautifulSoup) -> int:
        """
        Extrae el número de valoraciones del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            int: El número de valoraciones del libro.
        """
        rating_count = soup.select_one(BOOKS_RATING_COUNT_QUERY)
        return (
            get_integer(rating_count["content"])
            if rating_count and "content" in rating_count.attrs
            else 0
        )

    def _scrap_want_to_read_count(self, soup: BeautifulSoup) -> int:
        """
        Extrae el número de usuarios que quieren leer el libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            int: El número de usuarios que quieren leer el libro.
        """
        want_to_read_count = soup.select_one(BOOKS_WANT_TO_READ_COUNT_QUERY)
        return (
            get_integer(want_to_read_count.get_text(strip=True))
            if want_to_read_count
            else 0
        )

    def _scrap_read_count(self, soup: BeautifulSoup) -> int:
        """
        Extrae el número de usuarios que han leído el libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            int: El número de usuarios que han leído el libro.
        """
        read_count = soup.select_one(BOOKS_READ_COUNT_QUERY)
        return get_integer(read_count.get_text(strip=True)) if read_count else 0

    def _scrap_currently_reading_count(self, soup: BeautifulSoup) -> int:
        """
        Extrae el número de usuarios que están leyendo el libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            int: El número de usuarios que están leyendo el libro.
        """
        currently_reading_count = soup.select_one(BOOKS_CURRENTLY_READING_COUNT_QUERY)
        return (
            get_integer(currently_reading_count.get_text(strip=True))
            if currently_reading_count
            else 0
        )

    def _scrap_stats(self, soup: BeautifulSoup) -> tuple:
        """
        Extrae las estadísticas del libro como la valoración, el número de valoraciones, el número de usuarios que quieren leer el libro, el número de usuarios que han leído el libro y el número de usuarios que están leyendo el libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            tuple: Una tupla con la valoración, el número de valoraciones, el número de usuarios que quieren leer el libro, el número de usuarios que han leído el libro y el número de usuarios que están leyendo el libro.
        """
        stats = soup.select_one(BOOKS_STATS_QUERY)
        rating_value = None
        rating_count = None
        want_to_read_count = None
        read_count = None
        currently_reading_count = None
        if stats:
            rating_value = self._scrap_rating_value(soup)
            rating_count = self._scrap_rating_count(soup)
            want_to_read_count = self._scrap_want_to_read_count(soup)
            read_count = self._scrap_read_count(soup)
            currently_reading_count = self._scrap_currently_reading_count(soup)
        return (
            rating_value,
            rating_count,
            want_to_read_count,
            read_count,
            currently_reading_count,
        )

    def _scrap_working_id(self, soup: BeautifulSoup) -> str:
        """
        Extrae el ID del trabajo del libro.

        Args:
            soup (BeautifulSoup): El objeto BeautifulSoup que representa la página del libro.

        Returns:
            str: El ID del trabajo del libro.
        """
        working_id = soup.select_one(BOOKS_WORKING_ID_QUERY)
        return working_id.get_text(strip=True) if working_id else "Desconocido"

    def scrape_single_book(self, book_id: int, create_in_db: bool = True) -> dict:
        """
        Extrae la información de un solo libro dado su ID.
        Args:
            book_id (int): El ID del libro en Open Library.
        Returns:
            dict: Un diccionario con la información del libro.
        """
        open_library_id = f"OL{book_id}M"

        if create_in_db:
            existing_book = (
                self.db.query(Book)
                .filter(Book.open_library_id == open_library_id)
                .first()
            )
            if existing_book:
                return None
        url = f"{BASE_URL}/books/{open_library_id}"
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code != 200:
            logging.error(f"Error al acceder a {url}: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        title = self._scrap_title(soup)
        authors = self._scrap_authors(soup)
        subjects = self._scrap_subjects(soup, create_in_db=create_in_db)
        language, publish_date, publisher, pages = self._scrap_general_items(soup)

        (
            rating_value,
            rating_count,
            want_to_read_count,
            read_count,
            currently_reading_count,
        ) = self._scrap_stats(soup)
        working_id = self._scrap_working_id(soup)

        return {
            "id": book_id,
            "title": title,
            "authors": authors,
            "subjects": subjects,
            "language": language,
            "publish_year": publish_date,
            "publisher": publisher,
            "pages": pages,
            "rating": rating_value,
            "rating_count": rating_count,
            "want_to_read_count": want_to_read_count,
            "read_count": read_count,
            "currently_reading_count": currently_reading_count,
            "work_id": working_id,
            "open_library_id": open_library_id,
        }

    def _store_scraped_data(self, book_data: dict):
        """
        Almacena los datos de un libro en la base de datos.

        Args:
            book_data (dict): Los datos del libro a almacenar.
        """
        if not book_data:
            return

        new_book = Book(
            open_library_id=book_data["open_library_id"],
            work_id=book_data["working_id"],
            title=book_data["title"],
            publish_year=book_data["publish_date"],
            pages=book_data["pages"],
            language=book_data["language"],
            publisher=book_data["publisher"],
            authors=book_data["authors"],
            subjects=book_data["subjects"],
            rating=book_data["rating_value"],
            rating_count=book_data["rating_count"],
            want_to_read_count=book_data["want_to_read_count"],
            read_count=book_data["read_count"],
            currently_reading_count=book_data["currently_reading_count"],
        )
        self.db.add(new_book)

    def scrape_and_store_books_by_id_range(
        self,
        start_id: int,
        end_id: int,
        batch_size: int = 100,
        num_threads: int = 5,
    ):
        """
        Extrae y almacena libros en la base de datos en un rango de IDs especificado.

        Args:
            start_id (int): ID de inicio del rango.
            end_id (int): ID de fin del rango.
            batch_size (int, optional): Tamaño del batch para la extracción. Defaults to 100.
            num_threads (int, optional): Número de hilos a utilizar para la extracción. Defaults to 5.
        """
        total_books_added = 0
        for i in range(start_id, end_id, batch_size):
            id_batch = list(range(i, min(i + batch_size, end_id)))
            logging.info(f"Procesando batch de IDs: {id_batch[0]} a {id_batch[-1]}...")
            scraped_books = []
            with ThreadPoolExecutor(max_workers=num_threads) as executor:

                results = [
                    executor.submit(self.scrape_single_book, book_id)
                    for book_id in id_batch
                ]
                for future in as_completed(results):
                    book_data = future.result()
                    if book_data:
                        scraped_books.append(book_data)
                        total_books_added += 1
            try:
                book_author_relations = []
                book_subject_relations = []
                for book_data in scraped_books:
                    book_data["authors"] = author_singleton.bulk_get_or_create_author(
                        list(book_data["authors"]), self.db
                    )
                    book_author_relations.extend(
                        [
                            {"book_id": book_data["id"], "author_id": author.id}
                            for author in book_data["authors"]
                        ]
                    )
                    book_subject_relations.extend(
                        [
                            {"book_id": book_data["id"], "subject_id": subject.id}
                            for subject in book_data["subjects"]
                        ]
                    )
                book_singleton.bulk_create_books(scraped_books, self.db)
                if len(book_author_relations):
                    self.db.execute(
                        book_authors_association.insert(), book_author_relations
                    )
                if len(book_subject_relations):
                    self.db.execute(
                        book_subjects_association.insert(), book_subject_relations
                    )
                self.db.commit()
                logging.info(f"Se han agregado {total_books_added} a la base de datos")
            except Exception as e:
                logging.error(f"Error al hacer commit del batch: {e}")
                self.db.rollback()
        logging.info(f"Total de libros añadidos: {total_books_added}")

# Importa la Base desde su nueva ubicación
from app.settings.database import Base

# Importa cada uno de tus modelos
from .author import Author
from .book import Book
from .language import Language
from .subject import Subject

# URL base de Open Library
BASE_URL = "https://openlibrary.org"
HEADERS = {"Accept-Language": "es"}

# Soup queries
# Subjects
SUBJECTS_QUERY = "div#subjectsPage a[href*='/subjects/']"

# Books
BOOKS_NAME_QUERY = "h1.work-title"
BOOKS_AUTHOR_QUERY = "h2.edition-byline a[itemprop*='author']"
BOOKS_SUBJECT_QUERY = "div.subjects-content a[href*='/subjects/']"
BOOKS_ITEMS_QUERY = "div.edition-omniline"
BOOKS_LANGUAGE_QUERY = "a[href*='/languages/']"
BOOKS_PUBLISH_DATE_QUERY = "span[itemprop='datePublished']"
BOOKS_PUBLISHER_QUERY = "a[itemprop='publisher']"
BOOKS_PAGES_QUERY = "span[itemprop='numberOfPages']"
BOOKS_STATS_QUERY = "ul[itemprop='aggregateRating']"
BOOKS_RATING_VALUE_QUERY = "meta[itemprop='ratingValue']"
BOOKS_RATING_COUNT_QUERY = "meta[itemprop='ratingCount']"
BOOKS_WANT_TO_READ_COUNT_QUERY = "li.reading-log-stat:has(span.readers-stats__label:-soup-contains('Quiero leer')) span.readers-stats__stat"
BOOKS_READ_COUNT_QUERY = "li.reading-log-stat:has(span.readers-stats__label:-soup-contains('He leído')) span.readers-stats__stat"
BOOKS_CURRENTLY_READING_COUNT_QUERY = "li.reading-log-stat:has(span.readers-stats__label:-soup-contains('Actualmente leyendo')) span.readers-stats__stat"
BOOKS_WORKING_ID_QUERY = "dt:-soup-contains('Work ID') + dd"

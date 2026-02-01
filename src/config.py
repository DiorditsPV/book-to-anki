import os

OUTPUT_DIR = 'output'

BOOK_NAME = 'Dinniman_Dungeon-Crawler-Carl_1.epub'
DECK_NAME = 'Dungeon Crawler Carl En-Ru'

# CSV BUILD
OXFORD_PATH = os.path.join('data', 'dict', 'Oxford3000.txt')
BOOK = os.path.join('data', 'books', BOOK_NAME)
HANDLED_DIR = os.path.join(OUTPUT_DIR, 'handled_books')

# DECK BUILD
DECKS_DIR = os.path.join(OUTPUT_DIR, 'decks')
BOOK_BASENAME = BOOK_NAME.split(".")[0]
INPUT_COUNTER_CSV = os.path.join(HANDLED_DIR, f'{BOOK_BASENAME}_counter.csv')
DECK_FILEPATH = os.path.join(DECKS_DIR, f'{BOOK_BASENAME}.apkg')

for path in (HANDLED_DIR, DECKS_DIR):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
# Makefile
PYTHON = .venv/bin/python
PIP = .venv/bin/pip

# Установка зависимостей
install:
	python3 -m venv .venv
	$(PIP) install -U pip
	$(PIP) install nltk deep-translator genanki
	$(PYTHON) -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt'); nltk.download('punkt_tab')"

# Запуск основного скрипта (поиск слов)
run-main:
	$(PYTHON) src/main.py

# Сборка колоды Anki
run-anki:
	$(PYTHON) src/builder_deck.py

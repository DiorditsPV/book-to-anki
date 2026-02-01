import os
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from translator import translate_words_sync
from config import HANDLED_DIR, BOOK, OXFORD_PATH

def load_common_words(filepath):
    with open(filepath, 'r') as f:
        return set(line.strip().lower() for line in f)

def extract_text_from_fb2(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
    return " ".join(text.strip() for text in root.itertext() if text and text.strip())

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data and data.strip():
            self.parts.append(data.strip())

def extract_text_from_epub(filepath):
    parts = []
    with zipfile.ZipFile(filepath, 'r') as zf:
        for name in zf.namelist():
            lower_name = name.lower()
            content = zf.read(name).decode('utf-8', errors='ignore')
            parser = _HTMLTextExtractor()
            parser.feed(content)
            parts.extend(parser.parts)
    return " ".join(parts)

def get_filtered_counter(text, common_words):
    tokenizer = RegexpTokenizer(r"[A-Za-z]+(?:'[A-Za-z]+)?")
    lemmatizer = WordNetLemmatizer()
    words = tokenizer.tokenize(text.lower())
    
    lemmatized_words = [lemmatizer.lemmatize(w, pos='v') for w in words]
    
    filtered_words = [w for w in lemmatized_words if w not in common_words and len(w) > 3]
    return Counter(filtered_words)

def save_counter(counter, filepath):
    translations = {}
    words_for_translation = []
    for word, count in counter.most_common():
        if count <= 1:
            continue
        words_for_translation.append(word)
    translations = translate_words_sync(words_for_translation)

    with open(filepath, 'w', encoding='utf-8') as f:
        translated_count = 0
        for word, count in counter.most_common():
            if count <= 1:
                continue
                            
            translation = translations.get(word)
            if translation:
                line_content = f"{word},{translation},{count}"
                print(f"Translated ({translated_count + 1}): {word} -> {translation}")
                translated_count += 1
            else:
                line_content = f"{word},,{count}"
            
            f.write(f"{line_content}\n")

def main():

    print(f"Загружаеми 3k популярных слов: {OXFORD_PATH}")
    common_words = load_common_words(OXFORD_PATH)
    
    print(f"Исключаем слова из Oxford 3k: {BOOK}")
    book_ext = os.path.splitext(BOOK)[1].lower()
    if book_ext == '.fb2':
        book_text = extract_text_from_fb2(BOOK)
    elif book_ext == '.epub':
        book_text = extract_text_from_epub(BOOK)
        print(book_text[:6000])
    else:
        raise ValueError(f"Неподдерживаемый формат: {book_ext}")
    counter = get_filtered_counter(book_text, common_words)
    
    base_name = os.path.splitext(os.path.basename(BOOK))[0]
    os.makedirs(HANDLED_DIR, exist_ok=True)
    output_filename = os.path.join(HANDLED_DIR, f"{base_name}_counter.csv")
    
    print(f"Сохраняем по пути {output_filename}...")
    save_counter(counter, output_filename)

if __name__ == "__main__":
    main()

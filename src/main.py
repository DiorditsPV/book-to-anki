import os
import asyncio
import xml.etree.ElementTree as ET
from collections import Counter
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from deep_translator import GoogleTranslator

TRANSLATE_ENABLED = True
TRANSLATE_LIMIT = 800

def load_common_words(filepath):
    with open(filepath, 'r') as f:
        return set(line.strip().lower() for line in f)

def extract_text_from_fb2(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
    return " ".join(text.strip() for text in root.itertext() if text and text.strip())

def get_filtered_counter(text, common_words):
    tokenizer = RegexpTokenizer(r"[A-Za-z]+(?:'[A-Za-z]+)?")
    lemmatizer = WordNetLemmatizer()
    words = tokenizer.tokenize(text.lower())
    
    lemmatized_words = [lemmatizer.lemmatize(w, pos='v') for w in words]
    
    filtered_words = [w for w in lemmatized_words if w not in common_words and len(w) >= 3]
    return Counter(filtered_words)

async def translate_words(words, concurrency=10):
    semaphore = asyncio.Semaphore(concurrency)
    translations = {}

    async def translate_one(word):
        async with semaphore:
            return await asyncio.to_thread(
                lambda: GoogleTranslator(source='en', target='ru').translate(word)
            )

    tasks = {word: asyncio.create_task(translate_one(word)) for word in words}
    for word, task in tasks.items():
        try:
            translations[word] = await task
        except Exception:
            translations[word] = None
    return translations

def save_counter(counter, filepath, translate=False, translate_limit=0):
    translations = {}
    if translate:
        words_for_translation = []
        for word, count in counter.most_common():
            if count <= 1:
                continue
            words_for_translation.append(word)
            if translate_limit != 0 and len(words_for_translation) >= translate_limit:
                break
        translations = asyncio.run(translate_words(words_for_translation))

    with open(filepath, 'w', encoding='utf-8') as f:
        translated_count = 0
        for word, count in counter.most_common():
            if count <= 1:
                continue
                
            line_content = f"{word:40}, {count}"
            
            if translate and (translate_limit == 0 or translated_count < translate_limit):
                translation = translations.get(word)
                if translation:
                    line_content = f"{word:40}, {translation:40}, {count}"
                    print(f"Translated ({translated_count + 1}): {word} -> {translation}")
                    translated_count += 1
                else:
                    dumb = '--'
                    line_content = f"{word:40}, {dumb:40},{count:40}"
            
            f.write(f"{line_content}\n")

def main():
    common_words_path = os.path.join('data', 'dict', 'Oxford3000.txt')
    book_filename = os.path.join('data', 'books', 'Harry_Potter_and_the_Sorcerers_Stone.fb2')
    output_dir = 'output'

    print(f"Loading common words from: {common_words_path}")
    common_words = load_common_words(common_words_path)
    
    print(f"Processing book: {book_filename}")
    book_text = extract_text_from_fb2(book_filename)
    counter = get_filtered_counter(book_text, common_words)
    
    base_name = os.path.splitext(os.path.basename(book_filename))[0]
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"{base_name}_counter.txt")
    
    print(f"Saving to {output_filename} (Translation: {TRANSLATE_ENABLED}, Limit: {TRANSLATE_LIMIT})...")
    save_counter(counter, output_filename, translate=TRANSLATE_ENABLED, translate_limit=TRANSLATE_LIMIT)
    
    print(f"Done! Редкие слова из книги '{base_name}' (топ-50):")
    for word, count in counter.most_common(50):
        if count > 2:
            print(f"{word}: {count}")

if __name__ == "__main__":
    main()

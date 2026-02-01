import os
import xml.etree.ElementTree as ET
from collections import Counter
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from translator import translate_words_sync
from config import *

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
    print(f"Loading common words from: {common_words_path}")
    common_words = load_common_words(common_words_path)
    
    print(f"Processing book: {book_filename}")
    book_text = extract_text_from_fb2(book_filename)
    counter = get_filtered_counter(book_text, common_words)
    
    base_name = os.path.splitext(os.path.basename(book_filename))[0]
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"{base_name}_counter.csv")
    
    print(f"Saving to {output_filename}...")
    save_counter(counter, output_filename)
    
    print(f"Done! Редкие слова из книги '{base_name}' (топ-50):")
    for word, count in counter.most_common(50):
        if count > 2:
            print(f"{word}: {count}")

if __name__ == "__main__":
    main()

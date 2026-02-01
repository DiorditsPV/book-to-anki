import csv
import json
import os
import random
import genanki
from config import output_dir

INPUT_CSV = os.path.join(output_dir, 'Harry_Potter_and_the_Sorcerers_Stone_counter.txt')
DECK_NAME = 'Harry Potter Words Ru-En'
OUTPUT_APKG = os.path.join(output_dir, 'Harry_Potter.apkg')
IDS_PATH = os.path.join(output_dir, 'anki_ids.json')

def read_cards(csv_path):
    cards = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if not row or len(row) < 2:
                continue
            eng = row[0].strip()
            ru = row[1].strip()
            if not eng or not ru:
                continue
            cards.append((eng, ru))
    return cards

def load_or_create_ids(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('model_id'), data.get('deck_id')
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'model_id': model_id, 'deck_id': deck_id}, f)
    return model_id, deck_id

def build_deck(cards, model_id, deck_id):
    model = genanki.Model(
        model_id,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    deck = genanki.Deck(deck_id, DECK_NAME)
    for eng, ru in cards:
        note = genanki.Note(model=model, fields=[eng, ru])
        deck.add_note(note)
    return deck

def main():
    cards = read_cards(INPUT_CSV)
    model_id, deck_id = load_or_create_ids(IDS_PATH)
    deck = build_deck(cards, model_id, deck_id)
    deck.write_to_file(OUTPUT_APKG)

if __name__ == '__main__':
    main()


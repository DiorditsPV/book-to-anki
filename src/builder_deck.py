import csv
import random
import genanki
from config import INPUT_COUNTER_CSV, DECK_FILEPATH, DECK_NAME

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

def load_or_create_ids():
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)
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
    cards = read_cards(INPUT_COUNTER_CSV)
    model_id, deck_id = load_or_create_ids()
    deck = build_deck(cards, model_id, deck_id)
    deck.write_to_file(DECK_FILEPATH)

if __name__ == '__main__':
    main()


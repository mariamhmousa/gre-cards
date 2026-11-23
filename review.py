from db import update_card, DEFAULT_DB_PATH
from scheduler import sm_2

def review(card, rating, db_path=DEFAULT_DB_PATH):
    # card is a row from get_due_cards: (id, word, definition, example, repetition, interval, ef)
    # 1. unpack the card
    card_id, _, _, _, repetition, interval, ef = card
    # 2. call sm_2 with its repetition, interval, ef and the rating
    new_repetition, new_interval, new_ef = sm_2(repetition, interval, ef, rating)
    # 3. call update_card with the id and the new values
    update_card(card_id, new_repetition, new_interval, new_ef, db_path)
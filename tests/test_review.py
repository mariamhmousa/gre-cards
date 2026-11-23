from review import review
from db import init_db, add_card, get_due_cards
import sqlite3
import pytest

def test_review_card_successful(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "one's"
    definition = "This is a test."
    example = "One's example"
    add_card(word, definition, example, db_path)
    card = get_due_cards(db_path)[0]
    review(card, 4, db_path)
    assert get_due_cards(db_path) == []
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    rows = cur.execute("SELECT repetition, interval, ef FROM cards").fetchall()
    con.close()
    assert len(rows) == 1
    assert rows[0] == (1, 1, pytest.approx(2.5))


def test_review_card_failed(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "one's"
    definition = "This is a test."
    example = "One's example"
    add_card(word, definition, example, db_path)
    card = get_due_cards(db_path)[0]
    review(card, 2, db_path)
    assert get_due_cards(db_path) == []
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    rows = cur.execute("SELECT repetition, interval, ef FROM cards").fetchall()
    con.close()
    assert len(rows) == 1
    assert rows[0] == (0, 1, pytest.approx(2.18))

import sqlite3
from db import init_db, add_card, get_due_cards, update_card, get_card, import_cards
import datetime as dt
import pytest

def test_init_db_creates_table(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    result = cur.execute("SELECT name from sqlite_master WHERE type='table'")
    tables = result.fetchall()
    names = [row[0] for row in tables]
    con.close()
    assert "cards" in names

def test_init_db_twice(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    init_db(db_path)

def test_add_card(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "galore"
    definition = "an informal adjective that describes something as being in large numbers or amounts. It is always used postpositively, that is, after a noun."
    example = "The store promises bargains galore on Black Friday."
    today = dt.date.today().isoformat()
    add_card(word, definition, example, db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    result = cur.execute("SELECT word, definition, example, repetition, interval, ef, next_due from cards")
    rows = result.fetchall()
    assert len(rows) == 1
    assert rows[0] == (word, definition, example, 0, 0, 2.5, today)
    con.close()

def test_add_card_apstrophe(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "one's"
    definition = "This is to test apostrophes."
    example = "One's clothes"
    today = dt.date.today().isoformat()
    add_card(word, definition, example, db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    result = cur.execute("SELECT word, definition, example, repetition, interval, ef, next_due from cards")
    rows = result.fetchall()
    assert len(rows) == 1
    assert rows[0] == (word, definition, example, 0, 0, 2.5, today)
    con.close()

def test_newcard_due(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "one's"
    definition = "This is to test apostrophes."
    example = "One's clothes"
    add_card(word, definition, example, db_path)
    rows = get_due_cards(db_path)
    assert len(rows) == 1
    assert rows[0] == (1, word, definition, example, 0, 0, 2.5)

def test_future_due_date(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "one's"
    definition = "This is to test apostrophes."
    example = "One's clothes"
    future_due_date = dt.date(2999, 12, 30).isoformat()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("INSERT INTO cards (word, definition, example, next_due) VALUES (?, ?, ?, ?)",
        (word, definition, example, future_due_date))
    con.commit()
    con.close()
    rows = get_due_cards(db_path)
    assert len(rows) == 0

def test_future_and_due_cards(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word1 = "one's"
    definition1 = "This is a test."
    example1 = "example 1"
    word2 = "two's"
    definition2 = "This is a test."
    example2 = "example 2"
    future_due_date = dt.date(2999, 12, 30).isoformat()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("INSERT INTO cards (word, definition, example, next_due) VALUES (?, ?, ?, ?)",
        (word1, definition1, example1, future_due_date))
    con.commit()
    con.close()
    add_card(word2, definition2, example2, db_path)
    rows = get_due_cards(db_path)
    assert len(rows) == 1
    assert rows[0] == (2, word2, definition2, example2, 0, 0, 2.5)

def test_overdue_card(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word = "one's"
    definition = "This is a test."
    example = "example"
    overdue_date = dt.date(2000, 12, 30).isoformat()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("INSERT INTO cards (word, definition, example, next_due) VALUES (?, ?, ?, ?)",
        (word, definition, example, overdue_date))
    con.commit()
    con.close()
    rows = get_due_cards(db_path)
    assert len(rows) == 1
    assert rows[0] == (1, word, definition, example, 0, 0, 2.5)

def test_one_card_changes(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word1 = "Test"
    definition1 = "This is a test."
    example1 = "example"
    word2 = "Test2"
    definition2 = "This is a test again."
    example2 = "example2"
    add_card(word1, definition1, example1, db_path)
    add_card(word2, definition2, example2, db_path)
    update_card(1, 3, 6, 2.36, db_path)

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    result = cur.execute("SELECT id, repetition, interval, ef FROM cards ORDER BY id")
    rows = result.fetchall()
    con.close()
    assert len(rows) == 2
    assert rows[0] == (1, 3, 6, pytest.approx(2.36))
    assert rows[1] == (2, 0, 0, 2.5)

def test_next_due(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    word1 = "Test"
    definition1 = "This is a test."
    example1 = "example"
    add_card(word1, definition1, example1, db_path)
    update_card(1, 3, 6, 2.36, db_path)

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    result = cur.execute("SELECT id, repetition, interval, ef, next_due FROM cards")
    rows = result.fetchall()
    con.close()

    expected_next_due = (dt.date.today() + dt.timedelta(days = 6)).isoformat()
    assert len(rows) == 1
    assert rows[0] == (1, 3, 6, pytest.approx(2.36), expected_next_due)

def test_card_not_due(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    
    word1 = "Test"
    definition1 = "This is a test."
    example1 = "example"
    add_card(word1, definition1, example1, db_path)
    rows = get_due_cards(db_path)
    assert len(rows) == 1

    update_card(1, 2, 1, 2.5, db_path)
    rows = get_due_cards(db_path)
    assert len(rows) == 0

def test_get_card(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    word = "Test"
    definition = "This is a test."
    example = "example"

    add_card(word, definition, example, db_path)
    card = get_card(1, db_path)

    assert card == (1, word, definition, example, 0, 0, 2.5)

def test_get_nonexisting_card(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    word = "Test"
    definition = "This is a test."
    example = "example"

    add_card(word, definition, example, db_path)
    card = get_card(2, db_path)

    assert card is None

def test_import_cards(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    words_list = [("abate", "to lessen", "ex1"), ("brew", "to make tea", "ex2"), ("candid", "frank", "ex3")]
    count = import_cards(words_list, db_path)

    assert count == 3
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    result = cur.execute("SELECT word FROM cards")
    rows = result.fetchall()
    con.close()
    words = sorted(row[0] for row in rows)
    assert words == ["abate", "brew", "candid"]

def test_import_twice(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    words_list = [("abate", "to lessen", "ex1"), ("brew", "to make tea", "ex2"), ("candid", "frank", "ex3")]
    
    count = import_cards(words_list, db_path)
    assert count == 3
    
    count = import_cards(words_list, db_path)
    assert count == 0

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    result = cur.execute("SELECT word FROM cards")
    rows = result.fetchall()
    con.close()

    words = sorted(row[0] for row in rows)
    assert words == ["abate", "brew", "candid"]


def test_import_duplicates_in_same_list(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    words_list = [("abate", "to lessen", "ex1"), ("ABATE", "to lessen again", "ex2")]
    
    count = import_cards(words_list, db_path)
    assert count == 1

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    result = cur.execute("SELECT word, definition FROM cards")
    rows = result.fetchall()
    con.close()

    assert rows == [("abate", "to lessen")]

def test_import_apostrophes(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    words_list = [("one's", "a person's thing", "One's clothes")]
    
    count = import_cards(words_list, db_path)
    assert count == 1

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    result = cur.execute("SELECT word, definition, example FROM cards")
    rows = result.fetchall()
    con.close()

    assert rows == [("one's", "a person's thing", "One's clothes")]

def test_imported_cards_are_due(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    words_list = [("abate", "to lessen", "ex1"), ("brew", "to make tea", "ex2"), ("candid", "frank", "ex3")]
    
    count = import_cards(words_list, db_path)
    assert count == 3

    rows = get_due_cards(db_path)
    assert len(rows) == 3
    assert rows[0] == (1, "abate", "to lessen", "ex1", 0, 0, 2.5)
    assert rows[1] == (2, "brew", "to make tea", "ex2", 0, 0, 2.5)
    assert rows[2] == (3, "candid", "frank", "ex3", 0, 0, 2.5)

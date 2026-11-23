import sqlite3
import datetime as dt
DEFAULT_DB_PATH = "cards.db"

def init_db(db_path=DEFAULT_DB_PATH):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	cur.execute(
		'''CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY,
			word TEXT NOT NULL UNIQUE COLLATE NOCASE,
			definition TEXT,
			example TEXT,
			repetition INTEGER DEFAULT 0,
			interval INTEGER DEFAULT 0,
			ef REAL DEFAULT 2.5,
			next_due TEXT)'''
		)
	con.commit()
	con.close()

def add_card(word, definition, example, db_path=DEFAULT_DB_PATH):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	
	today = dt.date.today().isoformat()
	cur.execute("INSERT INTO cards (word, definition, example, next_due) VALUES (?, ?, ?, ?)",
		(word, definition, example, today))

	con.commit()
	con.close()

def import_cards(rows, db_path=DEFAULT_DB_PATH):
	con = sqlite3.connect(db_path)
	cur = con.cursor()

	today = dt.date.today().isoformat()
	rows_with_date = [(word, definition, example, today) for word, definition, example in rows]
	cur.executemany('''INSERT OR IGNORE INTO cards
		(word, definition, example, next_due) VALUES (?, ?, ?, ?)''',rows_with_date)
	con.commit()
	added = cur.rowcount
	con.close()
	return added

def get_due_cards(db_path=DEFAULT_DB_PATH):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	
	today = dt.date.today().isoformat()
	result = cur.execute("SELECT id, word, definition, example, repetition, interval, ef from cards WHERE next_due <= ? ORDER BY next_due, id", (today,))
	rows = result.fetchall()
	con.close()
	return rows

def update_card(card_id, repetition, interval, ef, db_path=DEFAULT_DB_PATH):
	con = sqlite3.connect(db_path)
	cur = con.cursor()

	new_next_due = (dt.date.today() + dt.timedelta(days = interval)).isoformat()
	cur.execute("UPDATE cards SET repetition = ?, interval = ?, ef = ?, next_due = ? WHERE id = ?",
		(repetition, interval, ef, new_next_due, card_id))

	con.commit()
	con.close()

def get_card(card_id, db_path=DEFAULT_DB_PATH):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    result = cur.execute("SELECT id, word, definition, example, repetition, interval, ef from cards WHERE id = ?", (card_id,))

    card = result.fetchone()
    con.close()

    return card

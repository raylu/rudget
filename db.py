import sqlite3

db = sqlite3.connect('rudget.db')
db.row_factory = sqlite3.Row
db.execute('PRAGMA foreign_keys = ON')

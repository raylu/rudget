CREATE TABLE IF NOT EXISTS plaid_item (
	id INTEGER PRIMARY KEY,
	item_id TEXT,
	access_token TEXT
);

CREATE TABLE IF NOT EXISTS plaid_transaction (
	id INTEGER PRIMARY KEY,
	transaction_id TEXT NOT NULL UNIQUE,
	date TEXT,
	name TEXT,
	amount INTEGER,
	category TEXT,
	UNIQUE(date, name, amount)
);

#!/usr/bin/env python3

from db import db
import plaid

def main():
	with db:
		cur = db.execute('SELECT access_token FROM plaid_item')
		while True:
			row = cur.fetchone()
			if row is None:
				break
			process_item(row['access_token'])

def process_item(access_token):
	transactions = []
	for t in plaid.iter_transactions(access_token):
		amount = int(t['amount'] * 100)
		category = ', '.join(t['category'])
		transactions.append((t['transaction_id'], t['date'], t['name'], amount, category))
		print('%s %-50s %9d %s' % (t['date'], t['name'], amount, category))
	db.executemany('''
		INSERT INTO plaid_transaction (transaction_id, date, name, amount, category) VALUES (?, ?, ?, ?, ?)
		ON CONFLICT(transaction_id) DO UPDATE SET
		date = excluded.date, name = excluded.name, amount = excluded.amount, category = excluded.category
	''', transactions)

if __name__ == '__main__':
	main()

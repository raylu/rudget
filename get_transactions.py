#!/usr/bin/env python3

from db import db
import plaid

def main():
	with db:
		cur = db.execute('SELECT access_token FROM plaid_item LIMIT 1')
		[[access_token]] = cur.fetchall()

		transactions = []
		for t in plaid.iter_transactions(access_token):
			amount = int(t['amount'] * 100)
			category = ', '.join(t['category'])
			transactions.append((t['transaction_id'], t['date'], t['name'], amount, category))
			print('%s %-50s %6d %s' % (t['date'], t['name'], amount, category))
		db.executemany('''
			INSERT INTO plaid_transaction (transaction_id, date, name, amount, category) VALUES (?, ?, ?, ?, ?)
			ON CONFLICT(transaction_id) DO UPDATE SET
			date = excluded.date, name = excluded.name, amount = excluded.amount, category = excluded.category
		''', transactions)

if __name__ == '__main__':
	main()

#!/usr/bin/env python3

from db import db
import plaid

def main():
	with db:
		cur = db.execute('SELECT access_token FROM plaid_item LIMIT 1')
		[[access_token]] = cur.fetchall()
	for t in plaid.iter_transactions(access_token):
		print(t['transaction_id'], t['date'])

if __name__ == '__main__':
	main()

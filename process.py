#!/usr/bin/env python3

import collections
from dataclasses import dataclass

from db import db
import plaid

def main():
	payees = collections.defaultdict(list)
	for t in iter_transactions():
		if t['amount'] < 0 or t['category'].startswith('Transfer,'):
			continue
		payees[t['name']].append(t)

	payee_tuples = sorted(payees.items(), key=lambda item: len(item[1]), reverse=True)
	for name, transactions in payee_tuples:
		print(name, len(transactions))

def iter_transactions():
	with db:
		cur = db.execute('''
			SELECT date, name, amount, category
			FROM plaid_transaction ORDER BY date ASC
		''')
		while True:
			row = cur.fetchone()
			if row is None:
				break
			yield row

if __name__ == '__main__':
	main()

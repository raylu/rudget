#!/usr/bin/env python3

import collections
from dataclasses import dataclass
import datetime

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
		if len(transactions) < 3:
			continue
		first = datetime.datetime.strptime(transactions[0]['date'], '%Y-%m-%d')

		last_date = datetime.datetime.strptime(transactions[1]['date'], '%Y-%m-%d')
		last_interval = last_date - first
		last_amount = transactions[1]['amount']
		periodic = non_periodic = 0
		for t in transactions[2:]:
			date = datetime.datetime.strptime(t['date'], '%Y-%m-%d')
			interval = date - last_date
			if is_periodic(interval, last_interval, t['amount'], last_amount):
				periodic += 1
			else:
				non_periodic += 1

			last_interval = interval
			last_date = date
			last_amount = t['amount']
		print(name, periodic, non_periodic)

def is_periodic(interval, last_interval, amount, last_amount):
	if interval.days < 20:
		return False
	if abs(interval - last_interval).days > 7:
		return False
	if abs(amount - last_amount) / last_amount > 0.4:
		return False
	return True

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

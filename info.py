#!/usr/bin/env python3

import collections
import datetime

def transaction_info(transactions, days):
	payees = collections.defaultdict(list)
	categories = collections.defaultdict(list)
	for t in transactions:
		if t.amount < 0:
			continue
		category = t.category.full_name
		if category.startswith('Transfer,') and not category.startswith('Transfer, Third Party'):
			continue
		if category == 'Payment, Credit Card':
			continue
		if t.name.startswith('FID BKG SVC LLC MONEYLINE PPD ID:'):
			continue
		payees[t.name].append(t)
		categories[category].append(t)

	transaction_threshold = datetime.date.today() - datetime.timedelta(days=days)
	total_spending = 0.0
	cat_by_periodicity = []
	for name, cat_transactions in categories.items():
		periodicity = group_periodicity(cat_transactions)
		displayed_transactions = []
		for t in cat_transactions:
			if t.date < transaction_threshold:
				continue
			displayed_transactions.append({
				'date': t.date.isoformat(), 'name': t.name, 'amount': t.amount, 'account': t.account.name,
			})
			total_spending += t.amount
		if len(displayed_transactions) > 0:
			cat_by_periodicity.append((name, periodicity, displayed_transactions))
	cat_by_periodicity.sort(key=lambda cbp: cbp[1])
	return cat_by_periodicity

def group_periodicity(transactions):
	if len(transactions) < 3:
		return 0.0

	first = transactions[0].date

	last_date = transactions[1].date
	last_interval = last_date - first
	last_amount = transactions[1].amount
	total_periodicity = 0.0
	for t in transactions[2:]:
		interval = t.date - last_date
		total_periodicity += transactions_periodicity(interval, last_interval, t.amount, last_amount)

		last_interval = interval
		last_date = t.date
		last_amount = t.amount
	return total_periodicity / (len(transactions) - 2)

def transactions_periodicity(interval, last_interval, amount, last_amount):
	periodicity = 0.0
	if interval.days > 20:
		periodicity += 0.2
	if abs(interval - last_interval).days < 7:
		periodicity += 0.4
	if abs(amount - last_amount) / last_amount < 0.4:
		periodicity += 0.4
	return periodicity

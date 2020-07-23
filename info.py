#!/usr/bin/env python3

import collections
import datetime

from sqlalchemy.orm import joinedload

import db

def transaction_info(user_id):
	payees = collections.defaultdict(list)
	categories = collections.defaultdict(list)
	for t in get_transactions(user_id):
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

	transaction_threshold = datetime.date.today() - datetime.timedelta(days=15 * 7)
	cat_by_periodicity = []
	for name, transactions in categories.items():
		periodicity = group_periodicity(transactions)
		transactions_list = []
		for t in transactions:
			if t.date < transaction_threshold:
				continue
			transactions_list.append({
				'date': t.date.isoformat(), 'name': t.name, 'amount': t.amount, 'account': t.account.name,
			})
		if len(transactions_list) > 0:
			cat_by_periodicity.append((name, periodicity, transactions_list))
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

def get_transactions(user_id):
	return db.PlaidTransaction.query \
		.join(db.PlaidTransaction.account) \
		.join(db.PlaidAccount.item) \
		.join(db.PlaidItem.user) \
		.filter(db.User.user_id == user_id) \
		.options(joinedload(db.PlaidTransaction.category), joinedload(db.PlaidTransaction.account)) \
		.all()

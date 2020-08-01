#!/usr/bin/env python3

import collections
import datetime

def transaction_info(transactions, accounts, days):
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
	items = items_dict(accounts)
	for name, cat_transactions in categories.items():
		periodicity = group_periodicity(cat_transactions)
		displayed_transactions = []
		for t in cat_transactions:
			if t.date < transaction_threshold:
				continue
			displayed_transactions.append({
				'date': t.date.isoformat(), 'name': t.name, 'amount': t.amount, 'account': t.account.name,
			})
			items[t.account.plaid_item_id]['accounts'][t.account.plaid_account_id]['total'] += t.amount
			total_spending += t.amount
		if len(displayed_transactions) > 0:
			cat_by_periodicity.append((name, periodicity, displayed_transactions))
	cat_by_periodicity.sort(key=lambda cbp: cbp[1])

	items_stripped = []
	for item in items.values():
		item['accounts'] = list(item['accounts'].values())
		items_stripped.append(item)
	return {'categories': cat_by_periodicity, 'items': items_stripped}

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

def items_dict(accounts):
	item_totals = {}
	account_totals = {}
	seen_accounts = set()
	last_item = None
	for account in accounts:
		if last_item is not None and account.item.plaid_item_id != last_item.plaid_item_id:
			item_totals[last_item.plaid_item_id] = {
				'name': last_item.name,
				'accounts': account_totals,
			}
			account_totals = {}
		key = (account.subtype, account.mask)
		if key in seen_accounts:
			total = None
		else:
			seen_accounts.add(key)
			total = 0
		account_totals[account.plaid_account_id] = {
			'name': account.name,
			'subtype': account.subtype,
			'mask': account.mask,
			'total': total,
		}
		last_item = account.item
	item_totals[last_item.plaid_item_id] = {
		'name': last_item.name,
		'accounts': account_totals,
	}
	return item_totals

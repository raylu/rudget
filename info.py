#!/usr/bin/env python3

import collections
import datetime
import operator

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
	months = collections.defaultdict(lambda: [0, 0, 0])
	items = items_dict(accounts)
	for name, cat_transactions in categories.items():
		periodicity = group_periodicity(cat_transactions)
		displayed_transactions = []
		for t in cat_transactions:
			if periodicity >= 0.5:
				regularity_group = 2
			elif periodicity >= 0.25:
				regularity_group = 1
			else:
				regularity_group = 0
			months[t.date.strftime('%Y-%m')][regularity_group] += t.amount
			if t.date >= transaction_threshold:
				displayed_transactions.append({
					'date': t.date.isoformat(),
					'name': t.name,
					'amount': t.amount,
					'account': t.account.name,
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
	return {'categories': cat_by_periodicity, 'items': items_stripped, 'months': months}

def group_periodicity(transactions):
	if len(transactions) < 3:
		return 0.0

	intervals = []
	last_date = transactions[0].date
	for t in transactions[1:]:
		intervals.append((t.date - last_date).days)
		last_date = t.date
	amounts = list(map(operator.attrgetter('amount'), transactions))
	date_variance = regularity(intervals)
	amount_variance = regularity(amounts)
	return (date_variance + amount_variance) / 2.0

def regularity(nums):
	total_irregularity = 0.0
	last_num = nums[0]
	for num in nums[1:]:
		difference = abs(num - last_num)
		if difference == 0:
			num_irregularity = 0.0
		else:
			try:
				num_irregularity = min(difference / ((num + last_num) / 2), 1.0)
			except ZeroDivisionError:
				num_irregularity = 1.0
		total_irregularity += num_irregularity
		last_num = num
	return 1.0 - total_irregularity / (len(nums) - 1)

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
	if last_item is not None:
		item_totals[last_item.plaid_item_id] = {
			'name': last_item.name,
			'accounts': account_totals,
		}
	return item_totals

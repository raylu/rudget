#!/usr/bin/env python3

import datetime
import sys

import httpx
from sqlalchemy.orm import load_only

import db
import plaid

def main():
	query = db.User.query
	if len(sys.argv) > 0:
		query.filter(db.User.user_id.in_(map(int, sys.argv[1:])))
	for user in query.all():
		process_user(user.user_id)

def process_user(user_id):
	transaction_query = db.PlaidTransaction.query \
			.join(db.PlaidTransaction.account) \
			.join(db.PlaidAccount.item) \
			.filter(db.PlaidItem.user_id == user_id) \
			.options(load_only(db.PlaidTransaction.transaction_id))
	plaid_transactions = frozenset(pt.transaction_id for pt in transaction_query.all())

	items = db.PlaidItem.query \
			.filter(db.PlaidItem.user_id == user_id) \
			.order_by(db.PlaidItem.plaid_item_id) \
			.all()
	seen_accounts = set()
	relogin_items = []
	for item in items:
		relogin = process_item(item, plaid_transactions, seen_accounts)
		if relogin:
			relogin_items.append(item)
	return relogin_items

def process_item(item, plaid_transactions, seen_accounts):
	try:
		accounts_response = plaid.get_accounts(item.access_token)
	except httpx.HTTPStatusError as e:
		if e.response.json()['error_code'] != 'ITEM_LOGIN_REQUIRED':
			raise
		print('plaid_item_id', item.plaid_item_id, 'needs relogin')
		return True
	plaid_accounts = handle_accounts(item.plaid_item_id, accounts_response)
	account_ids = []
	for plaid_account in plaid_accounts.values():
		key = (plaid_account.subtype, plaid_account.mask)
		if key not in seen_accounts:
			account_ids.append(plaid_account.account_id)
			seen_accounts.add(key)
		else:
			print('skipping', key)

	if len(account_ids) == 0:
		return
	print('getting transactions for plaid_item_id', item.plaid_item_id)
	transactions = plaid.TransactionIter(item.access_token, account_ids)

	for t in transactions:
		if t['category_id'] is None:
			print('ignoring', t)
			continue
		if t['transaction_id'] not in plaid_transactions:
			plaid_account_id = plaid_accounts[t['account_id']].plaid_account_id
			date = datetime.datetime.strptime(t['date'], '%Y-%m-%d').date()
			amount = int(t['amount'] * 100)
			plaid_transaction = db.PlaidTransaction(plaid_account_id=plaid_account_id,
					transaction_id=t['transaction_id'], date=date, name=t['name'],
					amount=amount, category_id=int(t['category_id']))
			db.session.add(plaid_transaction)
		#print('%s %-50s %9d %s' % (t['date'], t['name'], amount, ', '.join(t['category'])))
	db.session.commit()
	return False

def handle_accounts(item_id, accounts):
	plaid_accounts = {}
	for plaid_account in db.PlaidAccount.query.filter(db.PlaidAccount.plaid_item_id == item_id).all():
		plaid_accounts[plaid_account.account_id] = plaid_account

	for account in accounts:
		account_id = account['account_id']
		if account_id not in plaid_accounts:
			plaid_account = db.PlaidAccount(plaid_item_id=item_id, account_id=account_id,
				name=account['name'], mask=account['mask'], subtype=account['subtype'])
			db.session.add(plaid_account)
			plaid_accounts[account_id] = plaid_account
		else:
			plaid_account = plaid_accounts[account_id]
			plaid_account.name = account['name']
			plaid_account.mask = account['mask']
			plaid_account.subtype = account['subtype']

	db.session.flush()
	return plaid_accounts

if __name__ == '__main__':
	main()

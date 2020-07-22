#!/usr/bin/env python3

import db
import plaid

def main():
	items = db.PlaidItem.query.all()
	for item in items:
		process_item(item)

def process_item(item):
	print('getting transactions for', item.plaid_item_id)
	transactions = plaid.TransactionIter(item.access_token)
	plaid_accounts = handle_accounts(item.plaid_item_id, transactions.accounts)

	transaction_query = db.PlaidTransaction.query \
			.join(db.PlaidTransaction.account) \
			.filter(db.PlaidAccount.plaid_item_id == item.plaid_item_id)
	plaid_transactions = {}
	for plaid_transaction in transaction_query.all():
		key = (plaid_transaction.date, plaid_transaction.name, plaid_transaction.amount)
		plaid_transactions[key] = plaid_transaction

	for t in transactions:
		amount = int(t['amount'] * 100)
		key = (t['date'], t['name'], amount)
		if key not in plaid_transactions:
			plaid_account_id = plaid_accounts[t['account_id']].plaid_account_id
			plaid_transaction = db.PlaidTransaction(plaid_account_id=plaid_account_id,
					transaction_id=t['transaction_id'], date=t['date'], name=t['name'],
					amount=amount, category_id=int(t['category_id']))
			db.session.add(plaid_transaction)
		#print('%s %-50s %9d %s' % (t['date'], t['name'], amount, ', '.join(t['category'])))
	db.session.commit()

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

	return plaid_accounts

if __name__ == '__main__':
	main()

import datetime

import httpx

import config

hc = httpx.Client()

def exchange_token(public_token):
	data = _post('/item/public_token/exchange', json={
		'public_token': public_token,
	})
	return data['item_id'], data['access_token']

def link_token(user_id, access_token):
	data = _post('/link/token/create', json={
		'client_name': 'rudget',
		'access_token': access_token,
		'user': {'client_user_id': str(user_id)},
		'language': 'en',
		'country_codes': ['US'],
	})
	return data['link_token']

def auth(access_token):
	return _post('/auth/get', json={'access_token': access_token})

class TransactionIter:
	def __init__(self, access_token, account_ids):
		self.access_token = access_token
		self.account_ids = account_ids
		self.total_offset = 0
		self.data_offset = 0
		self.data = self.post()
		self.accounts = self.data['accounts']

	def post(self):
		return _post('/transactions/get', json={
			'access_token': self.access_token,
			'start_date': '2000-01-01',
			'end_date': str(datetime.date.today()),
			'options': {
				'account_ids': self.account_ids,
				'offset': self.total_offset,
				'count': 500,
			},
		})

	def __iter__(self):
		return self

	def __next__(self):
		if self.data_offset >= len(self.data['transactions']):
			self.total_offset += len(self.data['transactions'])
			if self.total_offset >= self.data['total_transactions']:
				raise StopIteration
			self.data = self.post()
			self.data_offset = 0

		transaction = self.data['transactions'][self.data_offset]
		self.data_offset += 1
		return transaction

def get_accounts(access_token):
	data = _post('/accounts/get', json={'access_token': access_token})
	return data['accounts']

def get_categories():
	# why does this require a JSON object?
	# https://github.com/plaid/plaid-python/blob/master/plaid/api/categories.py
	response = hc.post('https://%s.plaid.com/categories/get' % config.plaid.environment, json={})
	response.raise_for_status()
	return response.json()['categories']

def _post(endpoint, json):
	json.update({
		'client_id': config.plaid.client_id,
		'secret': config.plaid.development,
	})
	response = hc.post('https://%s.plaid.com%s' % (config.plaid.environment, endpoint), json=json)
	if response.status_code >= 300:
		raise httpx.HTTPStatusError(response.content, request=response._request, response=response)
	return response.json()

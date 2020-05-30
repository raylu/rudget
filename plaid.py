import datetime

import requests

import config

rs = requests.Session()

def exchange_token(public_token):
	data = _post('/item/public_token/exchange', json={
		'client_id': config.plaid.client_id,
		'secret': config.plaid.development,
		'public_token': public_token,
	})
	return data['item_id'], data['access_token']

def iter_transactions(access_token):
	offset = 0
	while True:
		data = _post('/transactions/get', json={
			'client_id': config.plaid.client_id,
			'secret': config.plaid.development,
			'access_token': access_token,
			'start_date': '2000-01-01',
			'end_date': str(datetime.date.today()),
			'options': {
				'offset': offset,
			},
		})
		for transaction in data['transactions']:
			yield transaction

		offset += len(data['transactions'])
		if offset >= data['total_transactions']:
			break

def _post(endpoint, json):
	response = rs.post('https://%s.plaid.com%s' % (config.plaid.environment, endpoint), json=json)
	response.raise_for_status()
	return response.json()

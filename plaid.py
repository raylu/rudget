import requests

import config

rs = requests.Session()

def exchange_token(public_token):
	response = rs.post('https://sandbox.plaid.com/item/public_token/exchange', json={
		'client_id': config.plaid.client_id,
		'secret': config.plaid.development,
		'public_token': public_token,
	})
	response.raise_for_status()
	data = response.json()
	return data['item_id'], data['access_token']

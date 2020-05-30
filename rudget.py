#!/usr/bin/env python3

import mimetypes
from os import path

from pigwig import PigWig, Response
import requests

import config

rs = requests.Session()

def root(request):
	return Response.render(request, 'root.jinja2', {'plaid_public_key': config.plaid.public_key})

def plaid_access_token(request):
	public_token = request.body['public_token']
	response = rs.post('https://sandbox.plaid.com/item/public_token/exchange', json={
		'client_id': config.plaid.client_id,
		'secret': config.plaid.development,
		'public_token': public_token,
	})
	response.raise_for_status()
	data = response.json()
	data['access_token']
	data['item_id']
	return Response.json(None)

def static(request, file_path):
	try:
		with open(path.join('static', file_path), 'rb') as f:
			content = f.read()
	except FileNotFoundError:
		return Response('not found', 404)
	content_type, _ = mimetypes.guess_type(file_path)
	return Response(body=content, content_type=content_type)

routes = [
	('GET', '/', root),
	('POST', '/plaid_access_token', plaid_access_token),
	('GET', '/static/<path:file_path>', static),
]

app = PigWig(routes, template_dir='templates')

if __name__ == '__main__':
	app.main()

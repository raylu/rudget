#!/usr/bin/env python3

import mimetypes
from os import path

from pigwig import PigWig, Response

import config
from db import db
import plaid

def root(request):
	return Response.render(request, 'root.jinja2', {
        'environment': config.plaid.environment,
        'plaid_public_key': config.plaid.public_key,
    })

def plaid_access_token(request):
	item_id, access_token = plaid.exchange_token(request.body['public_token'])
	with db:
		db.execute('INSERT INTO plaid_item (item_id, access_token) VALUES(?, ?)',
				(item_id, access_token))
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

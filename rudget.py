#!/usr/bin/env python3

import datetime
import mimetypes
from os import path
import traceback

from pigwig import PigWig, Response

import config
import db
import info
import plaid

def response_done_handler(request, response):
	try:
		db.session.rollback()
		db.session.remove()
	except Exception:
		traceback.print_exc()

def root(request):
	return Response.render(request, 'root.jinja2', {
        'environment': config.plaid.environment,
        'plaid_public_key': config.plaid.public_key,
    })

def login(request):
	email = request.body['email']
	password = request.body['password']
	if 'register' in request.body:
		user = db.User.register(email, password)
		db.session.commit()
	else:
		user = db.User.login(email, password)
	response = Response(code=303, location='/')
	response.set_secure_cookie(request, 'user_id', user.user_id, secure=True,
			max_age=datetime.timedelta(days=30))
	return response

def transaction_info(request):
	transaction_info = info.transaction_info()
	return Response.json(transaction_info)

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
	('POST', '/login', login),
	('GET', '/transaction_info', transaction_info),
	('POST', '/plaid_access_token', plaid_access_token),
	('GET', '/static/<path:file_path>', static),
]

app = PigWig(routes, template_dir='templates', cookie_secret=config.pigwig.cookie_secret.encode('ascii'),
		response_done_handler=response_done_handler)

if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	else:
		port = None
	app.main(port=port)

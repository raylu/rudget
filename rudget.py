#!/usr/bin/env python3

# pylint: disable=wrong-import-order,wrong-import-position,ungrouped-imports

import sys
if len(sys.argv) == 3 and sys.argv[2] == '--reload':
	if sys.platform == 'linux':
		import pigwig.reloader_linux as reloader
	elif sys.platform == 'darwin':
		import pigwig.reloader_osx as reloader
	reloader.init()

import eventlet
eventlet.monkey_patch()

import datetime
import mimetypes
from os import path
import traceback

import eventlet.wsgi
from pigwig import PigWig, Response
from sqlalchemy.orm import joinedload

import config
import db
import demo_transactions
import info
import plaid
import transactions

def response_done_handler(request, response):
	try:
		db.session.rollback()
		db.session.remove()
	except Exception:
		traceback.print_exc()

def root(request):
	user_id = request.get_secure_cookie('user_id', datetime.timedelta(days=30))
	return Response.render(request, 'root.jinja2', {'logged_in': user_id is not None})

def login(request):
	email = request.body['email']
	password = request.body['password']
	if 'register' in request.body:
		user = db.User.register(email, password)
		db.session.commit()
		location = '/accounts'
	else:
		user = db.User.login(email, password)
		if user is None:
			return Response('bad email/password', 403)
		location = '/outcomes'
	response = Response(code=303, location=location)
	response.set_secure_cookie(request, 'user_id', user.user_id, secure=True,
			max_age=datetime.timedelta(days=30))
	return response

def logout(request):
	response = Response(code=303, location='/')
	response.set_secure_cookie(request, 'user_id', None, secure=True, max_age=datetime.timedelta())
	return response

def outcomes(request):
	return Response.render(request, 'outcomes.jinja2', {})

def demo(request):
	return Response.render(request, 'outcomes.jinja2', {'demo': True})

def authed(view_fn):
	def wrapped(request):
		user_id = request.get_secure_cookie('user_id', datetime.timedelta(days=30))
		if user_id is None:
			return Response(code=401)
		return view_fn(request, int(user_id))
	return wrapped

@authed
def accounts(request, user_id):
	items = db.PlaidItem.query \
			.filter(db.PlaidItem.user_id == user_id) \
			.order_by(db.PlaidItem.plaid_item_id) \
			.options(joinedload(db.PlaidItem.accounts)) \
			.all()
	return Response.render(request, 'accounts.jinja2', {
        'environment': config.plaid.environment,
        'plaid_public_key': config.plaid.public_key,
		'items': items,
    })

@authed
def accounts_update(request, user_id):
	item = db.PlaidItem.query.get(int(request.body['plaid_item_id']))
	if item.user_id != user_id:
		return Response(code=403)
	item.name = request.body['name'] or None
	db.session.commit()
	return Response.json(True)

@authed
def fetch_transactions(request, user_id):
	relogin_items = transactions.process_user(user_id)
	if len(relogin_items) > 0:
		return Response.render(request, 'relogin.jinja2', {
			'environment': config.plaid.environment,
			'plaid_public_key': config.plaid.public_key,
			'relogin_items': relogin_items,
		})
	else:
		return Response(code=303, location='/outcomes')

@authed
def transaction_info(request, user_id):
	days = int(request.query['days'])
	plaid_transactions = db.PlaidTransaction.query \
		.join(db.PlaidTransaction.account) \
		.join(db.PlaidAccount.item) \
		.filter(db.PlaidItem.user_id == user_id) \
		.options(joinedload(db.PlaidTransaction.category), joinedload(db.PlaidTransaction.account)) \
		.order_by(db.PlaidTransaction.date) \
		.all()
	plaid_accounts = db.PlaidAccount.query \
			.join(db.PlaidAccount.item) \
			.filter(db.PlaidItem.user_id == user_id) \
			.order_by(db.PlaidItem.plaid_item_id) \
			.options(joinedload(db.PlaidAccount.item)) \
			.all()
	return Response.json(info.transaction_info(plaid_transactions, plaid_accounts, days))

def transaction_info_demo(request):
	days = int(request.query['days'])
	fake_transactions, fake_accounts = demo_transactions.data()
	return Response.json(info.transaction_info(fake_transactions, fake_accounts, days))

@authed
def plaid_access_token(request, user_id):
	item_id, access_token = plaid.exchange_token(request.body['public_token'])
	db.session.add(db.PlaidItem(user_id=user_id, item_id=item_id, access_token=access_token))
	db.session.commit()
	return Response.json(None)

@authed
def plaid_link_token(request, user_id):
	item = db.PlaidItem.query.get(int(request.body['plaid_item_id']))
	if item.user_id != user_id:
		return Response(code=403)
	link_token = plaid.link_token(user_id, item.access_token)
	return Response.json(link_token)

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
	('POST', '/logout', logout),
	('GET', '/outcomes', outcomes),
	('GET', '/demo', demo),
	('GET', '/accounts', accounts),
	('POST', '/accounts/update', accounts_update),
	('POST', '/fetch_transactions', fetch_transactions),
	('GET', '/transaction_info', transaction_info),
	('GET', '/transaction_info_demo', transaction_info_demo),
	('POST', '/plaid_access_token', plaid_access_token),
	('POST', '/plaid_link_token', plaid_link_token),
	('GET', '/static/<path:file_path>', static),
]

app = PigWig(routes, template_dir='templates', cookie_secret=config.pigwig.cookie_secret.encode('ascii'),
		response_done_handler=response_done_handler)

if __name__ == '__main__':
	if len(sys.argv) >= 2:
		port = int(sys.argv[1])
	else:
		port = None
	if len(sys.argv) == 3 and sys.argv[2] == '--reload':
		app.template_engine.jinja_env.auto_reload = True
	eventlet.wsgi.server(eventlet.listen(('127.1', port)), app)

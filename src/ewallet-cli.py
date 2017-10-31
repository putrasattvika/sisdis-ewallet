#!/usr/bin/env python2

import json
import argparse
import requests

from ewallet import helper

API_MAP= {
	'ping': 'ping',
	'register': 'register',
	'transfer': 'transfer',
	'get-saldo': 'getSaldo',
	'get-total-saldo': 'getTotalSaldo'
}

ARGUMENTS = {
	'id': 'user_id',
	'name': 'nama',
	'amount': 'nilai'
}

DB_FILE = 'ewallet.db'

DEFAULT_HEADERS = {
	'Content-Type': 'application/json',
	'Accept': 'application/json'
}

def get_args():
	parser = argparse.ArgumentParser()
	sp = parser.add_subparsers(dest='cmd')

	# Utils
	## python ewallet-cli.py ping <host>
	ping = sp.add_parser('ping')
	ping.add_argument('ip', metavar='IP', help="ewallet node IP")

	# Banking
	## python ewallet-cli.py register <host> <id> <name>
	register = sp.add_parser('register')
	register.add_argument('ip', metavar='IP', help="ewallet node IP")
	register.add_argument('id', metavar='ID', help="user ID/NPM")
	register.add_argument('name', metavar='NAME', help="user name")

	## python ewallet-cli.py transfer <host> <id> <amount>
	transfer = sp.add_parser('transfer')
	transfer.add_argument('ip', metavar='IP', help="ewallet node IP")
	transfer.add_argument('id', metavar='ID', help="user ID/NPM")
	transfer.add_argument('amount', metavar='amount', help="amount to transfer", type=int)

	# Query
	## python ewallet-cli.py get-saldo <host> <id>
	get_saldo = sp.add_parser('get-saldo')
	get_saldo.add_argument('ip', metavar='IP', help="ewallet node IP")
	get_saldo.add_argument('id', metavar='ID', help="user ID/NPM")

	## python ewallet-cli.py get-total-saldo <host> <id>
	get_total_saldo = sp.add_parser('get-total-saldo')
	get_total_saldo.add_argument('ip', metavar='IP', help="ewallet node IP")
	get_total_saldo.add_argument('id', metavar='ID', help="user ID/NPM")

	# Misc
	## python ewallet-cli.py list
	node_list = sp.add_parser('list')
	node_list.add_argument('--debug', action="store_true", help="debug mode")

	return parser.parse_args()

def ewallet_post(host, cmd, parameters):
	url = helper.url_utils.get_url(host, API_MAP[cmd])

	return requests.post(url, headers=DEFAULT_HEADERS, data=json.dumps(parameters)).json()

def handle(host, cmd, parameters):
	helper.db.init_db(DB_FILE)

	if cmd == 'ping' or cmd == 'get-total-saldo' or cmd == 'register':
		return ewallet_post(host, cmd, parameters)

	user = helper.db.get_user(parameters['user_id'])

	if not user:
		print '[!] user_id ({}) is not present in this node.'.format(parameters['user_id'])
		exit(1)

	if cmd == 'get-saldo':
		res = ewallet_post(host, cmd, parameters)

		if res['nilai_saldo'] == -1:
			ewallet_post(host, 'register', {'user_id': user['user_id'], 'nama': user['name']})
	elif cmd == 'transfer':
		if user['balance'] < parameters['nilai']:
			print '[!] Not enough balance for user_id ({}) in this node [balance={}, amount={}].' \
				.format(parameters['user_id'], user['balance'], parameters['nilai'])

			exit(1)

		res = ewallet_post(host, cmd, parameters)
		if res['status_transfer'] == 1:
			helper.db.alter_balance(user['user_id'], delta=-parameters['nilai'])
	else:
		res = ewallet_post(host, cmd, parameters)

	return res

def list_nodes(debug):
	helper.settings.set('DEBUG', debug)
	return helper.quorum_inquire()

def main():
	args = get_args()
	args_dict = vars(args)

	if args.cmd == 'list':
		print json.dumps(list_nodes(args.debug), indent=2, sort_keys=True)
		return

	parameters = {}
	for a in ARGUMENTS:
		if a in args_dict and args_dict[a] != None:
			parameters[ARGUMENTS[a]] = args_dict[a]

	print json.dumps(handle(args.ip, args.cmd, parameters), indent=2, sort_keys=True)

if __name__ == '__main__':
	main()
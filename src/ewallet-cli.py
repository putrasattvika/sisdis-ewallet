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
	'Content-Type': 'application/json'
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

	return parser.parse_args()

def ewallet_post(host, cmd, parameters):
	url = helper.url_utils.get_url(host, API_MAP[cmd])

	return requests.post(url, headers=DEFAULT_HEADERS, data=json.dumps(parameters), timeout=1).json()

def handle(host, cmd, parameters):
	helper.db.init_db(DB_FILE)

	if cmd == 'ping':
		return ewallet_post(host, cmd, parameters)

	user = helper.db.get_user(parameters['user_id'])

	if cmd != 'register' and not user:
		print '[!] user_id ({}) is not present in this node.'.format(parameters['user_id'])
		exit(1)

	res = ewallet_post(host, cmd, parameters)
	if cmd == 'get-saldo':
		if res['nilai_saldo'] == -1:
			ewallet_post(host, 'register', {'user_id': user['user_id'], 'nama': user['name']})

	return res

def main():
	args = get_args()
	args_dict = vars(args)

	parameters = {}
	for a in ARGUMENTS:
		if a in args_dict and args_dict[a] != None:
			parameters[ARGUMENTS[a]] = args_dict[a]

	print json.dumps(handle(args.ip, args.cmd, parameters), indent=2, sort_keys=True)

if __name__ == '__main__':
	main()
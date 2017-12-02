#!/usr/bin/env python2

import json
import pika
import time
import argparse
import requests

from ewallet import helper
from datetime import datetime

__DEFAULT_RABBITMQ_HOST = '172.17.0.3'
__DEFAULT_RABBITMQ_USER = 'sisdis'
__DEFAULT_RABBITMQ_PASS = 'sisdis'

API_MAP= {
	# 'ping': 'ping',
	'register': 'register',
	'transfer': 'transfer',
	'get-saldo': 'getSaldo',
	'get-total-saldo': 'getTotalSaldo'
}

DB_FILE = 'ewallet.db'

DEFAULT_HEADERS = {
	'Content-Type': 'application/json',
	'Accept': 'application/json'
}

MY_ID = '1406527532'

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--mq_host", help="rabbitmq host, default is {}".format(__DEFAULT_RABBITMQ_HOST), default=__DEFAULT_RABBITMQ_HOST)
	parser.add_argument("--mq_user", help="rabbitmq username, default is {}".format(__DEFAULT_RABBITMQ_USER), default=__DEFAULT_RABBITMQ_USER)
	parser.add_argument("--mq_pass", help="rabbitmq password, default is {}".format(__DEFAULT_RABBITMQ_PASS), default=__DEFAULT_RABBITMQ_PASS)
	parser.add_argument("--debug", "-d", action="store_true", help="debug mode, use local rabbitmq")

	sp = parser.add_subparsers(dest='cmd')

	# Utils
	## python ewallet-cli.py ping <host>
	# ping = sp.add_parser('ping')
	# ping.add_argument('ip', metavar='IP', help="ewallet node IP")

	# # Banking
	# ## python ewallet-cli.py register <host> <id> <name>
	# register = sp.add_parser('register')
	# register.add_argument('ip', metavar='IP', help="ewallet node IP")
	# register.add_argument('id', metavar='ID', help="user ID/NPM")
	# register.add_argument('name', metavar='NAME', help="user name")

	# ## python ewallet-cli.py transfer <host> <id> <amount>
	# transfer = sp.add_parser('transfer')
	# transfer.add_argument('ip', metavar='IP', help="ewallet node IP")
	# transfer.add_argument('id', metavar='ID', help="user ID/NPM")
	# transfer.add_argument('amount', metavar='amount', help="amount to transfer", type=int)

	# Query
	## python ewallet-cli.py get-saldo <host> <id>
	get_saldo = sp.add_parser('get-saldo')
	get_saldo.add_argument('node_id', metavar='NODE_ID', help="ewallet node ID")
	get_saldo.add_argument('user_id', metavar='USER_ID', help="user ID/NPM")

	# ## python ewallet-cli.py get-total-saldo <host> <id>
	# get_total_saldo = sp.add_parser('get-total-saldo')
	# get_total_saldo.add_argument('ip', metavar='IP', help="ewallet node IP")
	# get_total_saldo.add_argument('id', metavar='ID', help="user ID/NPM")

	# Misc
	## python ewallet-cli.py list
	node_list = sp.add_parser('list')
	node_list.add_argument('--debug', action="store_true", help="debug mode")

	return parser.parse_args()

def date2str(date):
	return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

def rmq_publish_receive(host, username, password, exchange, send_key, recv_key, body):
	cred = None
	if username and password:
		cred = pika.credentials.PlainCredentials(username, password)

	if cred:
		connection = pika.BlockingConnection(
			pika.ConnectionParameters(host=host, credentials=cred)
		)
	else:
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

	send_channel = connection.channel()
	send_queue = send_channel.queue_declare()
	send_channel.queue_bind(send_queue.method.queue, exchange, routing_key=send_key)

	recv_channel = connection.channel()
	recv_queue = recv_channel.queue_declare()
	recv_channel.queue_bind(recv_queue.method.queue, exchange, routing_key=recv_key)

	# publish
	# print 'sending with exchange={}, send_key={}'.format(exchange, send_key)
	send_channel.basic_publish(
		exchange=exchange,
		routing_key=send_key,
		body=body
	)

	# receive
	# print 'receiving with exchange={}, recv_key={}'.format(exchange, recv_key)
	cnt = 0
	while True:
		if cnt >= 10:
			body = '{"error": "no reply"}'
			break

		method, properties, body = recv_channel.basic_get(
			queue=recv_queue.method.queue,
			no_ack=True
		)

		if (method, properties, body) == (None, None, None):
			time.sleep(0.1)
			cnt += 1
		else:
			break

	recv_channel.queue_delete()
	send_channel.close()

	recv_channel.queue_delete()
	recv_channel.close()

	connection.close()

	return body

def handle(host, username, password, cmd, parameters):
	# if cmd == 'get-total-saldo' or cmd == 'register':
	# 	return ewallet_post(host, cmd, parameters)

	user = helper.db.get_user(parameters['user_id'])

	if not user:
		print '[!] user_id ({}) is not present in this node.'.format(parameters['user_id'])
		exit(1)

	if cmd == 'get-saldo':
		res = rmq_publish_receive(
			host, username, password, 'EX_GET_SALDO',
			'REQ_{}'.format(parameters['node_id']),
			'RESP_{}'.format(parameters['node_id']),
			json.dumps({
				"action": "get_saldo",
				"user_id": parameters['user_id'],
				"sender_id": MY_ID,
				"type": "request",
				"ts": date2str(datetime.now())
			})
		)

		# if res['nilai_saldo'] == -1:
		# 	ewallet_post(host, 'register', {'user_id': user['user_id'], 'nama': user['name']})
	# elif cmd == 'transfer':
	# 	if user['balance'] < parameters['nilai']:
	# 		print '[!] Not enough balance for user_id ({}) in this node [balance={}, amount={}].' \
	# 			.format(parameters['user_id'], user['balance'], parameters['nilai'])

	# 		exit(1)

	# 	res = ewallet_post(host, cmd, parameters)
	# 	if res['status_transfer'] == 1:
	# 		helper.db.alter_balance(user['user_id'], delta=-parameters['nilai'])
	# else:
	# 	res = ewallet_post(host, cmd, parameters)

	return json.loads(res)

def list_nodes():
	return helper.db.get_live_nodes()

def main():
	args = get_args()
	args_dict = vars(args)

	if args.debug:
		args.mq_host = '127.0.1.1'
		args.mq_user = None
		args.mq_pass = None

	helper.db.init_db(DB_FILE)

	if args.cmd == 'list':
		print json.dumps(list_nodes(), indent=2, sort_keys=True)
		return

	print json.dumps(handle(args.mq_host, args.mq_user, args.mq_pass, args.cmd, args_dict), indent=2, sort_keys=True)

if __name__ == '__main__':
	main()
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
	'register': 'register',
	'transfer': 'transfer',
	'get-saldo': 'get_saldo',
	'get-total-saldo': 'get_total_saldo'
}

DB_USER = 'ewallet'
DB_NAME = 'ewallet'
MY_ID = '1406527532'

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--mq_host", help="rabbitmq host, default is {}".format(__DEFAULT_RABBITMQ_HOST), default=__DEFAULT_RABBITMQ_HOST)
	parser.add_argument("--mq_user", help="rabbitmq username, default is {}".format(__DEFAULT_RABBITMQ_USER), default=__DEFAULT_RABBITMQ_USER)
	parser.add_argument("--mq_pass", help="rabbitmq password, default is {}".format(__DEFAULT_RABBITMQ_PASS), default=__DEFAULT_RABBITMQ_PASS)
	parser.add_argument("--debug", "-d", action="store_true", help="debug mode, use local rabbitmq")
	parser.add_argument("--raw", "-r", action="store_true", help="raw mode, no logical checking")

	sp = parser.add_subparsers(dest='cmd')

	# Banking
	## python ewallet-cli.py register <node_id> <user_id> <name>
	register = sp.add_parser('register')
	register.add_argument('node_id', metavar='NODE_ID', help="ewallet node ID")
	register.add_argument('user_id', metavar='USER_ID', help="user ID/NPM")
	register.add_argument('name', metavar='NAME', help="user name")

	## python ewallet-cli.py transfer <node_id> <user_id> <amount>
	transfer = sp.add_parser('transfer')
	transfer.add_argument('node_id', metavar='NODE_ID', help="ewallet node ID")
	transfer.add_argument('user_id', metavar='USER_ID', help="user ID/NPM")
	transfer.add_argument('amount', metavar='amount', help="amount to transfer", type=int)

	# Query
	## python ewallet-cli.py get-saldo <node_id> <user_id>
	get_saldo = sp.add_parser('get-saldo')
	get_saldo.add_argument('node_id', metavar='NODE_ID', help="ewallet node ID")
	get_saldo.add_argument('user_id', metavar='USER_ID', help="user ID/NPM")

	## python ewallet-cli.py get-total-saldo <node_id> <user_id>
	get_total_saldo = sp.add_parser('get-total-saldo')
	get_total_saldo.add_argument('node_id', metavar='NODE_ID', help="ewallet node ID")
	get_total_saldo.add_argument('user_id', metavar='USER_ID', help="user ID/NPM")

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

	recv_channel = connection.channel()
	recv_queue = recv_channel.queue_declare(auto_delete=True)
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

	send_channel.close()

	recv_channel.queue_delete()
	recv_channel.close()

	connection.close()

	return json.loads(body)

def handle(host, username, password, cmd, parameters, raw=False):
	user = helper.db.EWalletDB().get_user(parameters['user_id'])

	if not raw and not user and cmd != 'get-total-saldo' and cmd != 'register':
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

		if not raw and res['nilai_saldo'] == -1:
			rmq_publish_receive(
				host, username, password, 'EX_REGISTER',
				'REQ_{}'.format(parameters['node_id']),
				'RESP_{}'.format(parameters['node_id']),
				json.dumps({
					"action": "register",
					"user_id": user['user_id'],
					"nama": user['name'],
					"sender_id": MY_ID,
					"type": "request",
					"ts": date2str(datetime.now())
				})
			)
	elif cmd == 'get-total-saldo':
		res = rmq_publish_receive(
			host, username, password, 'EX_GET_TOTAL_SALDO',
			'REQ_{}'.format(parameters['node_id']),
			'RESP_{}'.format(parameters['node_id']),
			json.dumps({
				"action": "get_total_saldo",
				"user_id": parameters['user_id'],
				"sender_id": MY_ID,
				"type": "request",
				"ts": date2str(datetime.now())
			})
		)
	elif cmd == 'register':
		res = rmq_publish_receive(
			host, username, password, 'EX_REGISTER',
			'REQ_{}'.format(parameters['node_id']),
			'RESP_{}'.format(parameters['node_id']),
			json.dumps({
				"action": "register",
				"user_id": parameters['user_id'],
				"nama": parameters['name'],
				"sender_id": MY_ID,
				"type": "request",
				"ts": date2str(datetime.now())
			})
		)
	elif cmd == 'transfer':
		if not raw and (user['balance'] < parameters['amount']):
			print '[!] Not enough balance for user_id ({}) in this node [balance={}, amount={}].' \
				.format(parameters['user_id'], user['balance'], parameters['amount'])

			exit(1)

		res = rmq_publish_receive(
			host, username, password, 'EX_TRANSFER',
			'REQ_{}'.format(parameters['node_id']),
			'RESP_{}'.format(parameters['node_id']),
			json.dumps({
				"action": "transfer",
				"user_id": parameters['user_id'],
				"nilai": parameters['amount'],
				"sender_id": MY_ID,
				"type": "request",
				"ts": date2str(datetime.now())
			})
		)

		if not raw and res['status_transfer'] == 1:
			helper.db.EWalletDB().alter_balance(user['user_id'], delta=-parameters['amount'])
	# else:
	# 	res = ewallet_post(host, cmd, parameters)

	return res

def list_nodes(timestamp=None):
	return helper.db.EWalletDB().get_live_nodes(timestamp=timestamp)

def main():
	args = get_args()
	args_dict = vars(args)

	if args.debug:
		args.mq_host = '127.0.1.1'
		args.mq_user = None
		args.mq_pass = None

	helper.db.init(DB_USER, DB_NAME)

	if args.cmd == 'list':
		ts = time.time()

		print '[+] Live nodes at timestamp={:.0f} - 10secs'.format(ts)
		print json.dumps(list_nodes(timestamp=ts), indent=2, sort_keys=True)
		return

	print json.dumps(
		handle(
			args.mq_host, args.mq_user, args.mq_pass,
			args.cmd, args_dict, raw=args.raw
		), 
		indent=2,
		sort_keys=True
	)

if __name__ == '__main__':
	main()
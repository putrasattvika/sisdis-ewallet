#!/usr/bin/env python2
import time
import ewallet
import logging
import argparse

from ewallet.helper import settings
from ewallet.msgqueue import PingJob
from ewallet.msgqueue import GetSaldoJob
from ewallet.msgqueue import GetTotalSaldoJob
from ewallet.msgqueue import RegisterJob
from ewallet.msgqueue import TransferJob

__DEFAULT_ID = '1406527532'

__DEFAULT_PING_EXCHANGE = 'EX_PING'
__DEFAULT_PING_ROUTING_KEY = ''

__DEFAULT_GET_SALDO_EXCHANGE = 'EX_GET_SALDO'
__DEFAULT_GET_TOTAL_SALDO_EXCHANGE = 'EX_GET_TOTAL_SALDO'
__DEFAULT_REGISTER_EXCHANGE = 'EX_REGISTER'
__DEFAULT_TRANSFER_EXCHANGE = 'EX_TRANSFER'

__DEFAULT_RABBITMQ_HOST = '172.17.0.3'
__DEFAULT_RABBITMQ_USER = 'sisdis'
__DEFAULT_RABBITMQ_PASS = 'sisdis'

__DEFAULT_DB_USER = 'ewallet'
__DEFAULT_DB_NAME = 'ewallet'

logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger('ewallet.app')

def get_args():
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--id", "-i", help="node ID, default is {}".format(__DEFAULT_ID), default=__DEFAULT_ID)
	parser.add_argument("--debug", "-d", action="store_true", help="debug mode, use local rabbitmq")
	parser.add_argument("--docker", action="store_true", help="docker mode")
	parser.add_argument("--verbose", action="store_true", help="verbose mode")
	parser.add_argument("--help", action='help', help='print this help message')

	parser.add_argument("--mq_ping_ex", help="rabbitmq exchange for pings, default is {}".format(__DEFAULT_PING_EXCHANGE), default=__DEFAULT_PING_EXCHANGE)
	parser.add_argument("--mq_ping_key", help="rabbitmq routing key for pings, default is {}".format(__DEFAULT_PING_ROUTING_KEY), default=__DEFAULT_PING_ROUTING_KEY)

	parser.add_argument("--mq_get_saldo_ex", help="rabbitmq exchange for get saldo, default is {}".format(__DEFAULT_GET_SALDO_EXCHANGE), default=__DEFAULT_GET_SALDO_EXCHANGE)
	parser.add_argument("--mq_get_total_saldo_ex", help="rabbitmq exchange for get total saldo, default is {}".format(__DEFAULT_GET_TOTAL_SALDO_EXCHANGE), default=__DEFAULT_GET_TOTAL_SALDO_EXCHANGE)
	parser.add_argument("--mq_register_ex", help="rabbitmq exchange for register, default is {}".format(__DEFAULT_REGISTER_EXCHANGE), default=__DEFAULT_REGISTER_EXCHANGE)
	parser.add_argument("--mq_transfer_ex", help="rabbitmq exchange for transfer, default is {}".format(__DEFAULT_TRANSFER_EXCHANGE), default=__DEFAULT_TRANSFER_EXCHANGE)

	parser.add_argument("--mq_host", help="rabbitmq host, default is {}".format(__DEFAULT_RABBITMQ_HOST), default=__DEFAULT_RABBITMQ_HOST)
	parser.add_argument("--mq_user", help="rabbitmq username, default is {}".format(__DEFAULT_RABBITMQ_USER), default=__DEFAULT_RABBITMQ_USER)
	parser.add_argument("--mq_pass", help="rabbitmq password, default is {}".format(__DEFAULT_RABBITMQ_PASS), default=__DEFAULT_RABBITMQ_PASS)

	parser.add_argument("--db_user", help="database username, default is {}".format(__DEFAULT_DB_USER), default=__DEFAULT_DB_USER)
	parser.add_argument("--db_name", help="database name, default is {}".format(__DEFAULT_DB_NAME), default=__DEFAULT_DB_NAME)

	return parser.parse_args()

def main():
	args = get_args()
	format = '[%(asctime)s] %(levelname)s:%(name)s %(message)s'

	logging.basicConfig(format=format, level=logging.DEBUG if args.verbose else logging.INFO)

	logger.info('sttv_ewallet running with debug={} and id={}'.format(args.debug, args.id))

	ewallet.ewallet_init(args.db_user, args.db_name, str(args.id), debug=False)

	if args.debug:
		args.mq_host = '127.0.1.1'
		args.mq_user = None
		args.mq_pass = None

	if args.docker:
		args.mq_host = '172.21.0.1'
		args.mq_user = 'docker'
		args.mq_pass = 'docker'

	ewallet.helper.settings.set('mq_ping', {
		'exchange': args.mq_ping_ex,
		'key': args.mq_ping_key
	})

	ewallet.helper.settings.set('mq_get_saldo', {
		'exchange': args.mq_get_saldo_ex,
		'key': 'REQ_{}'.format(settings.NODE_ID)
	})

	ewallet.helper.settings.set('mq_get_total_saldo', {
		'exchange': args.mq_get_total_saldo_ex,
		'key': 'REQ_{}'.format(settings.NODE_ID)
	})

	ewallet.helper.settings.set('mq_register', {
		'exchange': args.mq_register_ex,
		'key': 'REQ_{}'.format(settings.NODE_ID)
	})

	ewallet.helper.settings.set('mq_transfer', {
		'exchange': args.mq_transfer_ex,
		'key': 'REQ_{}'.format(settings.NODE_ID)
	})

	bg_jobs = []
	bg_jobs.append( PingJob(args.mq_host, args.mq_user, args.mq_pass) )
	bg_jobs.append( GetSaldoJob(args.mq_host, args.mq_user, args.mq_pass) )
	bg_jobs.append( GetTotalSaldoJob(args.mq_host, args.mq_user, args.mq_pass) )
	bg_jobs.append( RegisterJob(args.mq_host, args.mq_user, args.mq_pass) )
	bg_jobs.append( TransferJob(args.mq_host, args.mq_user, args.mq_pass) )

	for job in bg_jobs:
		job.start()

	while True:
		try:
			time.sleep(10)
		except KeyboardInterrupt:
			logger.info('exiting, caugh KeyboardInterrupt')
			break
		except Exception as e:
			logger.info('exiting, caugh exception: {}'.format(e.message))
			break

	logger.info('stopping background jobs')
	for job in bg_jobs:
		job.stop()

if __name__ == '__main__':
	main()

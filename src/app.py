#!/usr/bin/env python2
import logging
import argparse
import connexion
import ewallet

from ewallet import *
from ewallet.msgqueue.ping import PingJob

__DEFAULT_ID = '1406527532'
__DEFAULT_HOST = '0.0.0.0'
__DEFAULT_PORT = 10034
__DEFAULT_PING_EXCHANGE = 'EX_PING'
__DEFAULT_PING_ROUTING_KEY = ''
__DEFAULT_RABBITMQ_HOST = '172.17.0.3'
__DEFAULT_RABBITMQ_USER = 'sisdis'
__DEFAULT_RABBITMQ_PASS = 'sisdis'

logger = logging.getLogger('ewallet.app')

def get_args():
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--id", "-i", help="node ID, default is {}".format(__DEFAULT_ID), default=__DEFAULT_ID)
	parser.add_argument("--host", "-h", help="host IP, default is {}".format(__DEFAULT_HOST), default=__DEFAULT_HOST)
	parser.add_argument("--port", "-p", help="listening port, default is {}".format(__DEFAULT_PORT), default=__DEFAULT_PORT)
	parser.add_argument("--mq_ping_ex", help="rabbitmq exchange for pings, default is {}".format(__DEFAULT_PING_EXCHANGE), default=__DEFAULT_PING_EXCHANGE)
	parser.add_argument("--mq_ping_key", help="rabbitmq routing key for pings, default is {}".format(__DEFAULT_PING_ROUTING_KEY), default=__DEFAULT_PING_ROUTING_KEY)
	parser.add_argument("--mq_host", help="rabbitmq host, default is {}".format(__DEFAULT_RABBITMQ_HOST), default=__DEFAULT_RABBITMQ_HOST)
	parser.add_argument("--mq_user", help="rabbitmq username, default is {}".format(__DEFAULT_RABBITMQ_USER), default=__DEFAULT_RABBITMQ_USER)
	parser.add_argument("--mq_pass", help="rabbitmq password, default is {}".format(__DEFAULT_RABBITMQ_PASS), default=__DEFAULT_RABBITMQ_PASS)
	parser.add_argument("--debug", "-d", action="store_true", help="debug mode, querying local node listing")
	parser.add_argument("--verbose", action="store_true", help="verbose mode")
	parser.add_argument("--help", action='help', help='print this help message')

	return parser.parse_args()

def main():
	args = get_args()
	logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

	ewallet_init('ewallet.db', str(args.id), debug=args.debug)

	validator_map = {
		'body': ewallet.helper.validation.FormJsonRequestBodyValidator,
		'parameter': connexion.decorators.validation.ParameterValidator
	}

	app = connexion.App(__name__, validator_map=validator_map)
	app.add_api('ewallet.yaml', strict_validation=True)

	logger.info('[+] sttv_ewallet running on {}:{} with debug={} and id={}'.format(args.host, args.port, args.debug, args.id))

	ping_job = PingJob(args.mq_ping_ex, args.mq_ping_key, args.mq_host, args.mq_user, args.mq_pass)
	ping_job.start()

	app.run(host=args.host, port=args.port, threaded=True)
	ping_job.stop()

if __name__ == '__main__':
	main()

#!/usr/bin/env python2
import logging
import argparse
import connexion

from ewallet import *

__DEFAULT_ID = '1406527532'
__DEFAULT_HOST = '0.0.0.0'
__DEFAULT_PORT = 10034

def get_args():
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--id", "-i", help="node ID, default is {}".format(__DEFAULT_ID), default=__DEFAULT_ID)
	parser.add_argument("--host", "-h", help="host IP, default is {}".format(__DEFAULT_HOST), default=__DEFAULT_HOST)
	parser.add_argument("--port", "-p", help="listening port, default is {}".format(__DEFAULT_PORT), default=__DEFAULT_PORT)
	parser.add_argument("--debug", "-d", action="store_true", help="debug mode, querying local node listing")
	parser.add_argument("--help", action='help', help='print this help message')

	return parser.parse_args()

def main():
	logging.basicConfig(level=logging.INFO)

	args = get_args()

	ewallet_init('ewallet.db', str(args.id), debug=args.debug)

	app = connexion.App(__name__)
	app.add_api('ewallet.yaml', strict_validation=True)

	print '[+] sttv_ewallet running on {}:{} with debug={} and id={}'.format(args.host, args.port, args.debug, args.id)
	app.run(host=args.host, port=args.port, threaded=True)

if __name__ == '__main__':
	main()
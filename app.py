#!/usr/bin/env python2
import connexion
import logging

from ewallet import *

def main():
	logging.basicConfig(level=logging.INFO)
	ewallet_init('ewallet.db')

	app = connexion.App(__name__)
	app.add_api('ewallet.yaml', strict_validation=True)

	app.run(threaded=True)

if __name__ == '__main__':
	main()
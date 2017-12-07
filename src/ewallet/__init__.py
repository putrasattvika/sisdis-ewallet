import os
import logging

from helper import db
from helper import settings

logger = logging.getLogger(__name__)

def ewallet_init(db_user, db_name, node_id, debug=False, whitelist_file='../conf/whitelist.txt'):
	db.init(db_user, db_name)

	settings.set('NODE_ID', node_id)
	settings.set('DEBUG', debug)

	settings.set('WHITELIST', [])
	if os.path.isfile(whitelist_file):
		with open(whitelist_file, 'r') as f:
			for npm in f.readlines():
				npm = npm.strip()

				if len(npm) > 0:
					settings.WHITELIST.append(npm)

	if len(settings.WHITELIST) == 0:
		settings.WHITELIST = None
	else:
		logger.info('using node_id whitelist: {}'.format(settings.WHITELIST))

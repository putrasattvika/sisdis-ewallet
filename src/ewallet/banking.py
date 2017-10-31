import logging

from helper import db
from helper import codes
from helper import quorum
from helper import definition

from helper.errors import *

logger = logging.getLogger('ewallet.banking')

@quorum(5, definition.register_response)
def register(body, healthy_nodes=[]):
	status_code = codes.UNKNOWN_ERROR

	try:
		if not db.create_user(body['user_id'], body['nama']):
			status_code = codes.UNKNOWN_ERROR
		else:
			status_code = codes.OK
	except DBUserAlreadyExistsError as e:
		status_code = codes.DATABASE_ERROR
		logger.info('[-] User already exsists: %s', e.message)
	except DBError as e:
		status_code = codes.DATABASE_ERROR
		logger.info('[-] Database error: %s', e.message)
	except Exception as e:
		status_code = codes.UNKNOWN_ERROR
		logger.info('[-] Unknown error: %s', e.message)

	return definition.register_response(status_code)

@quorum(5, definition.transfer_response)
def transfer(body, healthy_nodes=[]):
	status_code = codes.UNKNOWN_ERROR

	user_id = body['user_id']
	amount = body['nilai']

	try:
		user = db.get_user(user_id)

		if not user:
			status_code = codes.USER_DOES_NOT_EXISTS_ERROR
		elif amount < 0 or amount > 1000000000:
			status_code = codes.TRANSFER_AMT_ERROR
		else:
			db.alter_balance(user_id, delta=amount)
			status_code = codes.OK
	except DBError as e:
		status_code = codes.DATABASE_ERROR
		logger.info('[-] Database error: %s', e.message)
	except Exception as e:
		status_code = codes.UNKNOWN_ERROR
		logger.info('[-] Unknown error: %s', e.message)

	return definition.transfer_response(status_code)

import json
import logging
import requests
from multiprocessing.pool import ThreadPool

from helper import db
from helper import codes
from helper import quorum
from helper import settings
from helper import url_utils
from helper import definition

from helper.errors import *

logger = logging.getLogger('ewallet.query')
pool = ThreadPool(processes=4)

@quorum(5, definition.balance_inquiry_response)
def get_saldo(body, healthy_nodes=[]):
	balance = 0
	status_code = None

	user_id = body['user_id']

	try:
		user = db.get_user(user_id)

		if not user:
			status_code = codes.USER_DOES_NOT_EXISTS_ERROR
		else:
			balance = user['balance']
	except DBError as e:
		status_code = codes.DATABASE_ERROR
		logger.info('[-] Database error: %s', e.message)
	except Exception as e:
		status_code = codes.UNKNOWN_ERROR
		logger.info('[-] Unknown error: %s', e.message)

	return definition.balance_inquiry_response(balance, status_code=status_code)

def _get_node_saldo(ip, headers, data):
	url = url_utils.get_url(ip, url_utils.GET_BALANCE)
	res = requests.post(url, data=data, headers=headers, timeout=5).json()

	if res['nilai_saldo'] >= 0:
		return res['nilai_saldo']

	return 0

@quorum(8, definition.balance_inquiry_response)
def get_total_saldo(body, healthy_nodes=[]):
	balance = 0
	get_total_saldo_user_found = False
	status_code = None

	user_id = body['user_id']

	try:
		headers = { 'content-type': 'application/json', 'accept': 'application/json' }
		data = json.dumps({ 'user_id': user_id })

		if user_id == settings.NODE_ID:
			async_results = []
			for node in healthy_nodes:
				async_results.append( pool.apply_async(_get_node_saldo, (node['ip'],headers, data)) )

			for async in async_results:
				balance += async.get()
		else:
			for node in healthy_nodes:
				if node['npm'] == user_id:
					url = url_utils.get_url(node['ip'], url_utils.GET_TOTAL_BALANCE)
					res = requests.post(url, data=data, headers=headers, timeout=5).json()
					
					balance = res['nilai_saldo']
					get_total_saldo_user_found = True

			if not get_total_saldo_user_found:
				status_code = codes.USER_DOES_NOT_EXISTS_ERROR
	except requests.exceptions.RequestException as e:
		status_code = codes.NODE_UNREACHABLE_ERROR
		logger.info('[-] Node unreachable error: %s', e.message)
	except Exception as e:
		status_code = codes.UNKNOWN_ERROR
		logger.info('[-] Unknown error: %s', e.message)

	return definition.balance_inquiry_response(balance, status_code=status_code)

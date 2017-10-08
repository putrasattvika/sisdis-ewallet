import json
import requests

import banking

from helper import db
from helper import codes
from helper import quorum
from helper import url_utils
from helper import definition

from helper.errors import *

@quorum(5, definition.balance_inquiry_response)
def get_saldo(body, healthy_nodes=[]):
	balance = 0
	status_code = None

	user_id = body['user_id']

	try:
		user = db.get_user(user_id)

		if not user:
			status_code = codes.USER_DOES_NOT_EXISTS_ERROR
			banking.register({ 'user_id': user_id, 'nama': None })
		else:
			balance = user['balance']
	except DBError as e:
		status_code = codes.DATABASE_ERROR
	except Exception as e:
		status_code = codes.UNKNOWN_ERROR

	return definition.balance_inquiry_response(balance, status_code=status_code)

@quorum(8, definition.balance_inquiry_response)
def get_total_saldo(body, healthy_nodes=[]):
	balance = 0
	status_code = None

	user_id = body['user_id']

	for node in healthy_nodes:
		url = url_utils.get_url(node['ip'], url_utils.GET_BALANCE)
		headers = { 'content-type': 'application/json' }
		data = json.dumps({ 'user_id': user_id })

		try:
			res = requests.post(url, data=data, headers=headers, timeout=1).json()
			balance += res['nilai_saldo']
		except requests.exceptions.ConnectionError as e:
			status_code = codes.NODE_UNREACHABLE_ERROR
			break
		except Exception as e:
			status_code = codes.UNKNOWN_ERROR
			break

	return definition.balance_inquiry_response(balance, status_code=status_code)

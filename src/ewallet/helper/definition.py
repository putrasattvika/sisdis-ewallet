import time
import settings

from datetime import datetime
from codes import *

TRANSFER_RESPONSE_CODES = [
	OK, USER_DOES_NOT_EXISTS_ERROR, QUORUM_NOT_MET, DATABASE_ERROR,
	TRANSFER_AMT_ERROR, UNKNOWN_ERROR
]

REGISTER_RESPONSE_CODES = [
	OK, QUORUM_NOT_MET, DATABASE_ERROR, UNKNOWN_ERROR
]

BALANCE_INQUIRY_RESPONSE_CODES = [
	OK, USER_DOES_NOT_EXISTS_ERROR, QUORUM_NOT_MET, 
	NODE_UNREACHABLE_ERROR, DATABASE_ERROR, TRANSFER_AMT_ERROR,
	UNKNOWN_ERROR
]

PING_RESPONSE_CODES = [
	OK, UNKNOWN_ERROR
]

def date2str(date):
	return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

def transfer_response(status_code):
	if status_code not in TRANSFER_RESPONSE_CODES:
		raise ValueError('Invalid status code')

	return { "status_transfer": status_code }

def register_response(status_code):
	if status_code not in REGISTER_RESPONSE_CODES:
		raise ValueError('Invalid status code')

	return { "status_register": status_code }

def balance_inquiry_response(balance, status_code=None):
	if status_code:
		if status_code not in BALANCE_INQUIRY_RESPONSE_CODES:
			raise ValueError('Invalid status code')

		return { "nilai_saldo": status_code}

	return { "nilai_saldo": balance }

def ping_response(status_code):
	if status_code not in PING_RESPONSE_CODES:
		raise ValueError('Invalid status code')

	return { "pong": status_code }

def ping_mq_payload(timestamp = None):
	date = datetime.fromtimestamp(timestamp or time.time())
	
	return {
		"action": "ping",
		"npm": settings.NODE_ID,
		"ts": date2str(date)
	}

def balance_inquiry_response(balance, timestamp = None, status_code=None):
	date = datetime.fromtimestamp(timestamp or time.time())

	if status_code:
		if status_code not in BALANCE_INQUIRY_RESPONSE_CODES:
			raise ValueError('Invalid status code')

		balance = status_code

	return {
		"action": "get_saldo",
		"type": "response",
		"nilai_saldo": balance,
		"ts": date2str(date)
	}

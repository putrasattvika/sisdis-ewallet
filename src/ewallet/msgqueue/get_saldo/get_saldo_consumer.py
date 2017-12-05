import json
import logging

from ewallet.helper import db
from ewallet.helper import codes
from ewallet.helper import settings
from ewallet.helper import definition
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class GetSaldoConsumer(BaseConsumer):
	def __init__(self, connection_creator):
		super(GetSaldoConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback(ch, method, properties, body):
		try:
			logger.info('received get-saldo body=[{}]'.format(body))

			j = json.loads(body)

			exchange = settings.mq_get_saldo['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			try:
				user = db.EWalletDB().get_user(j['user_id'])

				balance = 0
				status_code = None
				if not user:
					status_code = codes.USER_DOES_NOT_EXISTS_ERROR
				else:
					balance = user['balance']
			except DBError as e:
				status_code = codes.DATABASE_ERROR
				logger.info('Database error: %s', e.message)
			except Exception as e:
				status_code = codes.UNKNOWN_ERROR
				logger.info('Unknown error: %s', e.message)

			response = json.dumps(definition.balance_inquiry_response(balance, status_code=status_code))

			logger.info('replying get-saldo to exchange={}, routing_key={}'.format(exchange, routing_key))
			ch.basic_publish(
				exchange = exchange,
				routing_key = routing_key,
				body = response
			)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

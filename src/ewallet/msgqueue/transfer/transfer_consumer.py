import json
import logging

from ewallet.helper import db
from ewallet.helper import codes
from ewallet.helper import settings
from ewallet.helper import definition
from ewallet.helper.errors import *
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class TransferConsumer(BaseConsumer):
	def __init__(self, connection_creator):
		super(TransferConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback(ch, method, properties, body):
		try:
			logger.info('received transfer body=[{}]'.format(body))

			j = json.loads(body)

			exchange = settings.mq_transfer['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			status_code = codes.UNKNOWN_ERROR
			user_id = j['user_id']
			amount = j['nilai']

			try:
				user = db.EWalletDB().get_user(user_id)

				if not user:
					status_code = codes.USER_DOES_NOT_EXISTS_ERROR
				elif amount < 0 or amount > 1000000000:
					status_code = codes.TRANSFER_AMT_ERROR
				else:
					db.EWalletDB().alter_balance(user_id, delta=amount)
					status_code = codes.OK
			except DBError as e:
				status_code = codes.DATABASE_ERROR
				logger.info('Database error: %s', e.message)
			except Exception as e:
				status_code = codes.UNKNOWN_ERROR
				logger.info('Unknown error: %s', e.message)

			response = json.dumps(definition.transfer_response(status_code))

			logger.info('replying transfer to exchange={}, routing_key={}'.format(exchange, routing_key))
			ch.basic_publish(
				exchange = exchange,
				routing_key = routing_key,
				body = response
			)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

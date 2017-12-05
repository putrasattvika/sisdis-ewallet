import json
import logging

from ewallet.helper import db
from ewallet.helper import codes
from ewallet.helper import settings
from ewallet.helper import definition
from ewallet.helper.errors import *
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class RegisterConsumer(BaseConsumer):
	def __init__(self, connection_creator):
		super(RegisterConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback(ch, method, properties, body):
		try:
			logger.info('received register body=[{}]'.format(body))

			j = json.loads(body)

			exchange = settings.mq_register['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			status_code = codes.UNKNOWN_ERROR

			try:
				if not db.EWalletDB().create_user(j['user_id'], j['nama']):
					status_code = codes.UNKNOWN_ERROR
				else:
					status_code = codes.OK
			except DBUserAlreadyExistsError as e:
				status_code = codes.DATABASE_ERROR
				logger.info('User already exsists: %s', e.message)
			except DBError as e:
				status_code = codes.DATABASE_ERROR
				logger.info('Database error: %s', e.message)
			except Exception as e:
				status_code = codes.UNKNOWN_ERROR
				logger.info('Unknown error: %s', e.message)

			response = json.dumps(definition.register_response(status_code))

			logger.info('replying register to exchange={}, routing_key={}'.format(exchange, routing_key))
			ch.basic_publish(
				exchange = exchange,
				routing_key = routing_key,
				body = response
			)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

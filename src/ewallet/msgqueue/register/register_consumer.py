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
	MINIMAL_QUORUM = 0.5

	def __init__(self, connection_creator):
		super(RegisterConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback_wrapper(ch, method, properties, body):
		quorum = db.EWalletDB().get_quorum()
		quorum_fulfilled = True

		if RegisterConsumer.MINIMAL_QUORUM:
			healthy_ratio = float(quorum['num_healthy'])/float(quorum['num_all'])
			if healthy_ratio < RegisterConsumer.MINIMAL_QUORUM:
				quorum_fulfilled = False

		RegisterConsumer.callback(ch, method, properties, body, quorum=quorum, quorum_fulfilled=quorum_fulfilled)

	@staticmethod
	def callback(ch, method, properties, body, quorum=None, quorum_fulfilled=False):
		try:
			logger.info('received register body=[{}]'.format(body))

			j = json.loads(body)
			exchange = settings.mq_register['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			status_code = codes.UNKNOWN_ERROR

			if not quorum_fulfilled:
				status_code = codes.QUORUM_NOT_MET
				response = response = json.dumps(definition.register_response(status_code))

				logger.info('replying quorum unfulfilled to exchange={}, routing_key={}'.format(exchange, routing_key))
				ch.basic_publish(
					exchange = exchange,
					routing_key = routing_key,
					body = response
				)

				return

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

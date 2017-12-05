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
	MINIMAL_QUORUM = 0.5

	def __init__(self, connection_creator):
		super(TransferConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback_wrapper(ch, method, properties, body):
		quorum = db.EWalletDB().get_quorum()
		quorum_fulfilled = True

		if TransferConsumer.MINIMAL_QUORUM:
			healthy_ratio = float(quorum['num_healthy'])/float(quorum['num_all'])
			if healthy_ratio < TransferConsumer.MINIMAL_QUORUM:
				quorum_fulfilled = False

		TransferConsumer.callback(ch, method, properties, body, quorum=quorum, quorum_fulfilled=quorum_fulfilled)

	@staticmethod
	def callback(ch, method, properties, body, quorum=None, quorum_fulfilled=False):
		try:
			logger.info('received transfer body=[{}]'.format(body))

			j = json.loads(body)
			exchange = settings.mq_transfer['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			status_code = codes.UNKNOWN_ERROR

			if not quorum_fulfilled:
				status_code = codes.QUORUM_NOT_MET
				response = json.dumps(definition.transfer_response(status_code))

				logger.info('replying quorum unfulfilled to exchange={}, routing_key={}'.format(exchange, routing_key))
				ch.basic_publish(
					exchange = exchange,
					routing_key = routing_key,
					body = response
				)

				return

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

import json
import logging

from ewallet.helper import db
from ewallet.helper import codes
from ewallet.helper import settings
from ewallet.helper import definition
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class GetSaldoConsumer(BaseConsumer):
	MINIMAL_QUORUM = 0.5

	def __init__(self, connection_creator):
		super(GetSaldoConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback_wrapper(ch, method, properties, body):
		quorum = db.EWalletDB().get_quorum()
		quorum_fulfilled = True

		if GetSaldoConsumer.MINIMAL_QUORUM:
			healthy_ratio = float(quorum['num_healthy'])/float(quorum['num_all'])
			if healthy_ratio < GetSaldoConsumer.MINIMAL_QUORUM:
				quorum_fulfilled = False

		GetSaldoConsumer.callback(ch, method, properties, body, quorum=quorum, quorum_fulfilled=quorum_fulfilled)

	@staticmethod
	def callback(ch, method, properties, body, quorum=None, quorum_fulfilled=False):
		try:
			logger.info('received get-saldo body=[{}]'.format(body))

			j = json.loads(body)
			exchange = settings.mq_get_saldo['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			balance = 0
			status_code = None

			if not quorum_fulfilled:
				status_code = codes.QUORUM_NOT_MET
				response = json.dumps(definition.balance_inquiry_response(balance, status_code=status_code))

				logger.info('replying quorum unfulfilled to exchange={}, routing_key={}'.format(exchange, routing_key))
				ch.basic_publish(
					exchange = exchange,
					routing_key = routing_key,
					body = response
				)

				return

			try:
				user = db.EWalletDB().get_user(j['user_id'])

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

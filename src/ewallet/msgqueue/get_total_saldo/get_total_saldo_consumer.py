import json
import logging

from datetime import datetime
from ewallet.helper import db
from ewallet.helper import codes
from ewallet.helper import common
from ewallet.helper import settings
from ewallet.helper import definition
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class GetTotalSaldoConsumer(BaseConsumer):
	CALLBACK_CONN_CREATOR = None

	def __init__(self, connection_creator):
		super(GetTotalSaldoConsumer, self).__init__(connection_creator)

		GetTotalSaldoConsumer.CALLBACK_CONN_CREATOR = connection_creator

	@staticmethod
	def callback(ch, method, properties, body):
		quorum = db.EWalletDB().get_quorum()
		GetTotalSaldoConsumer._callback(ch, method, properties, body, quorum=quorum)

	@staticmethod
	def _callback(ch, method, properties, body, quorum=None):
		try:
			logger.info('received get-total-saldo body=[{}]'.format(body))

			j = json.loads(body)

			connection_creator = GetTotalSaldoConsumer.CALLBACK_CONN_CREATOR

			exchange = settings.mq_get_total_saldo['exchange']
			get_saldo_exchange = settings.mq_get_saldo['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			user_id = j['user_id']
			balance = 0
			status_code = None
			get_total_saldo_user_found = False

			try:
				if user_id == settings.NODE_ID:
					recv_conns = []
					for node in quorum['healthy_nodes']:
						conn, channel, queue = connection_creator.rmq_publish(
							get_saldo_exchange,
							'REQ_{}'.format(node['npm']),
							json.dumps({
								"action": "get_saldo",
								"user_id": user_id,
								"sender_id": settings.NODE_ID,
								"type": "request",
								"ts": common.date2str(datetime.now())
							}),
							recv_key='RESP_{}'.format(settings.NODE_ID)
						)
						recv_conns.append((conn, channel, queue, node['npm']))

					for conn, channel, queue, npm in recv_conns:
						res = connection_creator.rmq_consume(conn, channel, queue)

						if 'nilai_saldo' in res:
							if res['nilai_saldo'] >= 0:
								balance += res['nilai_saldo']
						else:
							status_code = codes.NODE_UNREACHABLE_ERROR
							logger.info('Node {} returned invalid body: {}'.format(npm, res))
							break
				else:
					for node in quorum['healthy_nodes']:
						if node['npm'] == user_id:
							res = connection_creator.rmq_publish_consume(
								exchange,
								'REQ_{}'.format(node['npm']),
								'RESP_{}'.format(settings.NODE_ID),
								json.dumps({
									"action": "get_total_saldo",
									"user_id": user_id,
									"sender_id": settings.NODE_ID,
									"type": "request",
									"ts": common.date2str(datetime.now())
								})
							)

							balance = res['nilai_saldo']
							get_total_saldo_user_found = True

					if not get_total_saldo_user_found:
						status_code = codes.USER_DOES_NOT_EXISTS_ERROR
			except Exception as e:
				status_code = codes.UNKNOWN_ERROR
				logger.info('Unknown error: %s', e.message)

			response = json.dumps(definition.total_balance_inquiry_response(balance, status_code=status_code))

			logger.info('replying get-total-saldo to exchange={}, routing_key={}'.format(exchange, routing_key))
			ch.basic_publish(
				exchange = exchange,
				routing_key = routing_key,
				body = response
			)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

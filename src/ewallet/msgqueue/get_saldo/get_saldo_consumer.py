import json
import logging

from ewallet.helper import db
from ewallet.helper import settings
from ewallet.helper import definition
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class GetSaldoConsumer(BaseConsumer):
	def __init__(self, connection_creator):
		super(GetSaldoConsumer, self).__init__(
			connection_creator,
			settings.mq_get_saldo['exchange'],
			routing_key='REQ_{}'.format(settings.NODE_ID)
		)

	@staticmethod
	def callback(ch, method, properties, body):
		try:
			logger.info('received get-saldo body=[{}]'.format(body))

			j = json.loads(body)

			exchange = settings.mq_get_saldo['exchange']
			routing_key = 'RESP_{}'.format(j['sender_id'])

			balance = -1
			user = db.get_user(j['user_id'])
			if user:
				balance = user['balance']

			response = json.dumps(definition.balance_inquiry_response(balance))

			reply_queue = ch.queue_declare()
			ch.queue_bind(
				reply_queue.method.queue,
				exchange,
				routing_key=routing_key
			)

			logger.info('replying get-saldo to exchange={}, routing_key={}'.format(exchange, routing_key))
			ch.basic_publish(
				exchange = exchange,
				routing_key = routing_key,
				body = response
			)

			ch.queue_delete(queue=reply_queue.method.queue)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

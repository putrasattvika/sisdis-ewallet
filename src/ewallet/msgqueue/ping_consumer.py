import json
import pika
import logging
import threading

from datetime import datetime
from ewallet.helper import db

logger = logging.getLogger('ewallet.app')

class PingConsumer(object):
	def __init__(self, connection_creator):
		super(PingConsumer, self).__init__()

		self.connection_creator = connection_creator

	def start(self):
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.daemon = True
		self.is_running = True

		self.thread.start()

	def stop(self):
		self.is_running = False
		self.channel.stop_consuming()
		self.thread.join(timeout=2)

	@staticmethod
	def callback(ch, method, properties, body):
		try:
			j = json.loads(body)
			dt = datetime.strptime(j['ts'], '%Y-%m-%d %H:%M:%S')
			ts = int((dt - datetime.fromtimestamp(0)).total_seconds())

			db.update_node_ping(j['npm'], ts)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

	def run(self):
		while self.is_running:
			try:
				self.channel, self.queue = self.connection_creator.get_connection()
				logger.info('Consuming to {}'.format(self.queue.method.queue))

				self.channel.basic_consume(PingConsumer.callback, queue=self.queue.method.queue, no_ack=True)
				self.channel.start_consuming()
			except Exception as e:
				logger.info('error@consumer_run, body=[{}], errmsg=[{}]'.format(body, e.message))

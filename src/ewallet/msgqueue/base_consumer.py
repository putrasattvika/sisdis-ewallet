import pika
import logging
import threading

class BaseConsumer(object):
	def __init__(self, connection_creator, exchange='', routing_key=None):
		super(BaseConsumer, self).__init__()

		self.connection_creator = connection_creator
		self.exchange = exchange
		self.routing_key = routing_key

		self.logger = logging.getLogger(__name__ + '::' + self.__class__.__name__)

	def start(self):
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.daemon = True
		self.is_running = True

		self.thread.start()

	def stop(self):
		self.is_running = False
		self.channel.stop_consuming()
		self.thread.join(timeout=1)

	@staticmethod
	def callback(ch, method, properties, body):
		raise NotImplementedError

	def run(self):
		while self.is_running:
			self.logger.info('Getting new channel: exchange={}, routing_key={}'.format(self.exchange, self.routing_key))
			self.channel, self.queue = self.connection_creator.get_new_channel()
			self.channel.queue_bind(self.queue.method.queue, self.exchange, routing_key=self.routing_key)

			try:
				self.logger.info('Consuming to {}'.format(self.queue.method.queue))

				self.channel.basic_consume(self.__class__.callback, queue=self.queue.method.queue, no_ack=True)
				self.channel.start_consuming()
			except Exception as e:
				self.logger.info('error@consumer_run, errmsg=[{}]'.format(e.message))

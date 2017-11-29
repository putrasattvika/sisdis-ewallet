import pika

from ping_consumer import PingConsumer
from ping_publisher import PingPublisher

class PingJob(object):
	def __init__(self, exchange, routing_key, host, username, password, publish_interval=3):
		super(PingJob, self).__init__()
		
		self.exchange = exchange
		self.routing_key = routing_key
		self.host = host
		self.cred = pika.credentials.PlainCredentials(username, password)

		self.connection_creator = ConnectionCreator(host, username, password)
		self.publisher = PingPublisher(self.connection_creator, exchange, routing_key, interval=publish_interval)
		self.consumer = PingConsumer(self.connection_creator)
		
	def start(self):
		self.publisher.start()
		self.consumer.start()

	def stop(self):
		self.publisher.stop()
		self.consumer.stop()
		self.connection_creator.close()

class ConnectionCreator(object):
	def __init__(self, host, username, password,):
		super(ConnectionCreator, self).__init__()

		self.host = host
		self.cred = pika.credentials.PlainCredentials(username, password)

		self.conn = None
		self.channel, self.queue = (None, None)
		self.channel, self.queue = self.get_connection()

	def close(self):
		if self.channel: 
			self.channel.queue_delete()
			self.channel.close()
			self.conn.close()

	def get_connection(self):
		try:
			if self.channel and self.channel.is_open:
				return self.channel, self.queue

			if self.queue and self.queue.queue_declare(queue=self.queue.method.queue):
				return self.channel, self.queue
		except:
			pass

		self.conn = pika.BlockingConnection(
			pika.ConnectionParameters(host=self.host, credentials=self.cred)
		)

		self.channel = self.conn.channel()
		self.queue = self.channel.queue_declare()

		return self.channel, self.queue

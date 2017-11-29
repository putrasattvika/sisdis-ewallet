import pika
import json
import time
import logging
import threading

from ewallet.helper import codes
from ewallet.helper import definition

class PingPublisher(object):
	def __init__(self, connection_creator, exchange, routing_key, interval=3):
		super(PingPublisher, self).__init__()

		self.connection_creator = connection_creator
		self.exchange = exchange
		self.routing_key = routing_key
		self.interval = interval

	def start(self):
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.daemon = True
		self.is_running = True

		self.thread.start()

	def stop(self):
		if self.is_running:
			self.is_running = False
			self.thread.join()

	def run(self):
		while self.is_running:
			self.channel, self.queue = self.connection_creator.get_connection()
			self.channel.queue_bind(self.queue.method.queue, self.exchange)

			self.channel.basic_publish(
				exchange = self.exchange,
				routing_key = self.routing_key,
				body = json.dumps(definition.ping_mq_payload())
			)

			time.sleep(self.interval)

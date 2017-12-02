import pika

from ewallet.msgqueue.base_job import BaseJob
from ping_consumer import PingConsumer
from ping_publisher import PingPublisher

class PingJob(BaseJob):
	def __init__(self, host, username, password, publish_interval=3):
		super(PingJob, self).__init__(host, username, password)

		self.publisher = PingPublisher(self.connection_creator, interval=publish_interval)
		self.consumer = PingConsumer(self.connection_creator)
		
	def start(self):
		self.publisher.start()
		self.consumer.start()

	def stop(self):
		self.publisher.stop()
		self.consumer.stop()
		self.connection_creator.close()

import pika

from ewallet.helper import settings
from ewallet.msgqueue.base_job import BaseJob
from ewallet.msgqueue.base_job import ConnectionCreator

from register_consumer import RegisterConsumer

class RegisterJob(BaseJob):
	def __init__(self, host, username, password):
		super(RegisterJob, self).__init__(host, username, password)

		self.connection_creator = ConnectionCreator(
			host, username, password,
			settings.mq_register['exchange'],
			routing_key=settings.mq_register['key']
		)

		self.consumer = RegisterConsumer(self.connection_creator)
		
	def start(self):
		self.consumer.start()

	def stop(self):
		self.consumer.stop()
		self.connection_creator.close()

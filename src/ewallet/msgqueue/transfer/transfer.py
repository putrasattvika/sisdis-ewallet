import pika

from ewallet.helper import settings
from ewallet.msgqueue.base_job import BaseJob
from ewallet.msgqueue.base_job import ConnectionCreator

from transfer_consumer import TransferConsumer

class TransferJob(BaseJob):
	def __init__(self, host, username, password):
		super(TransferJob, self).__init__(host, username, password)

		self.connection_creator = ConnectionCreator(
			host, username, password,
			settings.mq_transfer['exchange'],
			routing_key=settings.mq_transfer['key']
		)

		self.consumer = TransferConsumer(self.connection_creator)
		
	def start(self):
		self.consumer.start()

	def stop(self):
		self.consumer.stop()
		self.connection_creator.close()

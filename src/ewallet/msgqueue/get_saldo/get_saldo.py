import pika

from ewallet.helper import settings
from ewallet.msgqueue.base_job import BaseJob
from ewallet.msgqueue.base_job import ConnectionCreator

from get_saldo_consumer import GetSaldoConsumer

class GetSaldoJob(BaseJob):
	def __init__(self, host, username, password):
		super(GetSaldoJob, self).__init__(host, username, password)

		self.connection_creator = ConnectionCreator(
			host, username, password,
			settings.mq_get_saldo['exchange'],
			routing_key=settings.mq_get_saldo['key']
		)

		self.consumer = GetSaldoConsumer(self.connection_creator)
		
	def start(self):
		self.consumer.start()

	def stop(self):
		self.consumer.stop()
		self.connection_creator.close()

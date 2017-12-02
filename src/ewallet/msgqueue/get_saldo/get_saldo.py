import pika

from ewallet.msgqueue.base_job import BaseJob
from get_saldo_consumer import GetSaldoConsumer

class GetSaldoJob(BaseJob):
	def __init__(self, host, username, password):
		super(GetSaldoJob, self).__init__(host, username, password)

		self.consumer = GetSaldoConsumer(self.connection_creator)
		
	def start(self):
		self.consumer.start()

	def stop(self):
		self.consumer.stop()
		self.connection_creator.close()

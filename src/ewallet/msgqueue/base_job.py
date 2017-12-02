import pika

class BaseJob(object):
	def __init__(self, host, username, password):
		super(BaseJob, self).__init__()
		
		self.host = host
		self.connection_creator = ConnectionCreator(host, username, password)
		
	def start(self):
		pass

	def stop(self):
		pass

class ConnectionCreator(object):
	def __init__(self, host, username, password):
		super(ConnectionCreator, self).__init__()

		self.host = host

		self.cred = None
		if username and password:
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

		if self.cred:
			self.conn = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.host, credentials=self.cred)
			)
		else:
			self.conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))

		self.channel = self.conn.channel()
		self.queue = self.channel.queue_declare()

		return self.channel, self.queue

	def get_new_channel(self):
		channel, queue = self.get_connection()

		if self.cred:
			conn = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.host, credentials=self.cred)
			)
		else:
			conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))

		return conn.channel(), queue

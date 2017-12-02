import pika

class BaseJob(object):
	def __init__(self, host, username, password):
		super(BaseJob, self).__init__()
		
		self.host = host
		
	def start(self):
		pass

	def stop(self):
		pass

class ConnectionCreator(object):
	def __init__(self, host, username, password, exchange, routing_key=''):
		super(ConnectionCreator, self).__init__()

		self.host = host
		self.exchange = exchange
		self.routing_key = routing_key

		self.cred = None
		if username and password:
			self.cred = pika.credentials.PlainCredentials(username, password)

		self.connections = {}

	def close(self):
		for identifier in self.connections:
			try:
				queue_name = self.connections[identifier]['queue'].method.queue
				self.connections[identifier]['channel'].queue_delete(queue=queue_name)
				self.connections[identifier]['channel'].close()
				self.connections[identifier]['connection'].close()
			except:
				pass

	def get_connection(self, identifier):
		if identifier in self.connections:
			channel = self.connections[identifier]['channel']
			queue = self.connections[identifier]['queue']

			try:
				if channel and channel.is_open:
					# if queue and queue.queue_declare(queue=queue.method.queue):
					return channel, queue
			except:
				pass

		if self.cred:
			conn = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.host, credentials=self.cred)
			)
		else:
			conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))

		channel = conn.channel()
		queue = channel.queue_declare()
		channel.queue_bind(queue.method.queue, self.exchange, routing_key=self.routing_key)

		self.connections[identifier] = {
			'connection': conn,
			'channel': channel,
			'queue': queue
		}

		return channel, queue

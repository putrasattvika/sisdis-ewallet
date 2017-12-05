import json
import time
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
		queue = channel.queue_declare(auto_delete=True)
		channel.queue_bind(queue.method.queue, self.exchange, routing_key=self.routing_key)

		self.connections[identifier] = {
			'connection': conn,
			'channel': channel,
			'queue': queue
		}

		return channel, queue

	def rmq_publish(self, exchange, send_key, body, recv_key=None):
		if self.cred:
			connection = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.host, credentials=self.cred)
			)
		else:
			connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))

		send_channel = connection.channel()

		if recv_key:
			recv_channel = connection.channel()
			recv_queue = recv_channel.queue_declare(auto_delete=True)
			recv_channel.queue_bind(recv_queue.method.queue, exchange, routing_key=recv_key)

		# publish
		send_channel.basic_publish(
			exchange=exchange,
			routing_key=send_key,
			body=body
		)

		send_channel.close()

		if recv_key:
			return connection, recv_channel, recv_queue
		else:
			return None

	def rmq_consume(self, connection, recv_channel, recv_queue, ack=False, left_open=False):
		# receive
		cnt = 0
		while True:
			if cnt >= 10:
				body = '{"error": "no reply"}'
				break

			method, properties, body = recv_channel.basic_get(
				queue=recv_queue.method.queue,
				no_ack=ack
			)

			if (method, properties, body) == (None, None, None):
				time.sleep(0.1)
				cnt += 1
			else:
				break

		if not left_open:
			recv_channel.queue_delete()
			recv_channel.close()
			connection.close()

		return json.loads(body)

	def rmq_publish_consume(self, exchange, send_key, recv_key, body):
		connection, recv_channel, recv_queue = self.rmq_publish(exchange, send_key, body, recv_key=recv_key)
		return self.rmq_consume(connection, recv_channel, recv_queue)

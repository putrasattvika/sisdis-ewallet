import json
import logging

from datetime import datetime
from ewallet.helper import db
from ewallet.helper import settings
from ewallet.msgqueue.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)

class PingConsumer(BaseConsumer):
	def __init__(self, connection_creator):
		super(PingConsumer, self).__init__(connection_creator)

	@staticmethod
	def callback(ch, method, properties, body):
		try:
			j = json.loads(body)
			dt = datetime.strptime(j['ts'], '%Y-%m-%d %H:%M:%S')
			ts = int((dt - datetime.fromtimestamp(0)).total_seconds())

			db.update_node_ping(j['npm'], ts)
		except Exception as e:
			logger.info('error@consumer_callback, body=[{}], errmsg=[{}]'.format(body, e.message))

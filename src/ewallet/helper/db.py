import time
import psycopg2
import settings

from errors import *
from contextlib import contextmanager

class EWalletDB(object):
	__instance = None

	def __new__(cls):
		if cls.__instance == None:
			cls.__instance = object.__new__(cls)
		return cls.__instance

	def __init__(self):
		super(EWalletDB, self).__init__()

	def set(self, user, dbname):
		self.user = user
		self.dbname = dbname
		self.init_db()

	@contextmanager
	def db_cursor(self, commit=True):
		conn = psycopg2.connect("dbname={} user={}".format(self.dbname, self.user))

		yield conn.cursor()

		if commit: conn.commit()
		conn.close()

	def init_db(self):
		with self.db_cursor() as c:
			c.execute('''
				CREATE TABLE IF NOT EXISTS account (
					user_id		varchar,
					name		varchar,
					balance		varchar,
					PRIMARY KEY (user_id)
				)
			''')

			c.execute('''
				CREATE TABLE IF NOT EXISTS nodes (
					npm			varchar,
					timestamp	int,
					PRIMARY KEY (npm)
				)
			''')

	def get_user(self, user_id):
		with self.db_cursor(commit=False) as c:
			query = '''
				SELECT user_id, name, balance
				FROM account
				WHERE user_id=%s;
			'''

			c.execute(query, (user_id, ))
			result = c.fetchone()

		if not result:
			return None

		return {
			'user_id': result[0],
			'name': result[1],
			'balance': int(result[2])
		}
	
	def create_user(self, user_id, name, balance=0):
		if self.get_user(user_id):
			raise DBUserAlreadyExistsError('User {} already exists'.format(user_id))

		with self.db_cursor() as c:
			query = '''
				INSERT INTO account (user_id, name, balance) 
				VALUES ( %s, %s, %s );
			'''

			c.execute(query, (user_id, name, str(balance)))

		return self.get_user(user_id)

	def alter_balance(self, user_id, balance=None, delta=None):
		if not balance and not delta:
			raise ValueError('Balance and delta are unspecified')

		user = self.get_user(user_id)

		if not user:
			raise DBUserNotFoundError('User {} not found'.format(user_id))

		if balance:
			final_balance = str(balance)
		elif delta:
			final_balance = str(user['balance'] + delta)

		with self.db_cursor() as c:
			query = '''
				UPDATE account SET balance=%s
				WHERE user_id=%s;
			'''

			c.execute(query, (final_balance, user_id))

		return self.get_user(user_id)

	def update_node_ping(self, npm, timestamp):
		with self.db_cursor() as c:
			query = '''
				INSERT INTO nodes (npm, timestamp)
				VALUES ( %s, %s )
				ON CONFLICT(npm) DO UPDATE
					SET timestamp = excluded.timestamp;
			'''

			c.execute(query, (npm, timestamp))

	def get_live_nodes(self, time_limit_secs=10, timestamp=None):
		ts = timestamp or time.time()

		with self.db_cursor(commit=False) as c:
			query = '''
				SELECT npm, timestamp
				FROM nodes
				WHERE timestamp >= %s
			'''

			if settings.WHITELIST and len(settings.WHITELIST) > 0:
				query += '''
					AND npm in ({})
				'''.format(', '.join(["'" + x +"'" for x in settings.WHITELIST]))

			query += ';'

			c.execute(query, (ts - time_limit_secs, ))
			q_result = c.fetchall()

		result = []
		for qr in q_result:
			result.append({
				'npm': qr[0],
				'last_ts': qr[1]
			})

		return result

	def get_quorum(self, time_limit_secs=10, timestamp=None):
		ts = timestamp or time.time()

		with self.db_cursor(commit=False) as c:
			query = '''
				SELECT count(npm)
				FROM nodes
			'''

			if settings.WHITELIST and len(settings.WHITELIST) > 0:
				query += '''
					WHERE npm in ({})
				'''.format(', '.join(["'" + x +"'" for x in settings.WHITELIST]))

			query += ';'

			c.execute(query)
			q_result = c.fetchone()

		total_nodes = int(q_result[0])
		healthy_nodes = self.get_live_nodes(time_limit_secs=time_limit_secs, timestamp=timestamp)

		return {
			'healthy_nodes': healthy_nodes,
			'num_healthy': len(healthy_nodes),
			'num_all': total_nodes
		}

def init(user, dbname):
	ewallet_db = EWalletDB()
	ewallet_db.set(user, dbname)

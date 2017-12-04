import time
import sqlite3

from errors import *

def init_db(dbfile):
	globals()['__DBFILE'] = dbfile

	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	c.execute('''
		CREATE TABLE IF NOT EXISTS ewallet (
			user_id		text,
			name		text,
			balance		text,
			PRIMARY KEY (user_id)
		)
	''')

	c.execute('''
		CREATE TABLE IF NOT EXISTS ewallet_nodes (
			npm			text,
			timestamp	integer,
			PRIMARY KEY (npm)
		)
	''')	

	conn.commit()
	conn.close()

def get_user(user_id):
	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		SELECT user_id, name, balance
		FROM ewallet
		WHERE user_id=?;
	'''

	c.execute(query, (user_id, ))
	result = c.fetchone()
	conn.close()

	if not result:
		return None

	return {
		'user_id': result[0],
		'name': result[1],
		'balance': int(result[2])
	}

def create_user(user_id, name, balance=0):
	if get_user(user_id):
		raise DBUserAlreadyExistsError('User {} already exists'.format(user_id))

	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		INSERT INTO ewallet (user_id, name, balance) 
		VALUES ( ?, ?, ? );
	'''

	c.execute(query, (user_id, name, str(balance)))

	conn.commit()
	conn.close()

	return get_user(user_id)

def alter_balance(user_id, balance=None, delta=None):
	if not balance and not delta:
		raise ValueError('Balance and delta are unspecified')

	user = get_user(user_id)

	if not user:
		raise DBUserNotFoundError('User {} not found'.format(user_id))

	if balance:
		final_balance = str(balance)
	elif delta:
		final_balance = str(user['balance'] + delta)

	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		UPDATE ewallet SET balance=?
		WHERE user_id=?;
	'''

	c.execute(query, (final_balance, user_id))

	conn.commit()
	conn.close()

	return get_user(user_id)

def update_node_ping(npm, timestamp):
	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		INSERT OR REPLACE INTO ewallet_nodes (npm, timestamp)
		VALUES ( ?, ? );
	'''

	c.execute(query, (npm, timestamp))

	conn.commit()
	conn.close()

def get_live_nodes(time_limit_secs=10, timestamp=None):
	ts = timestamp or time.time()

	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		SELECT npm, timestamp
		FROM ewallet_nodes
		WHERE timestamp >= ?;
	'''

	c.execute(query, (ts - time_limit_secs, ))
	q_result = c.fetchall()
	conn.close()

	result = []
	for qr in q_result:
		result.append({
			'npm': qr[0],
			'last_ts': qr[1]
		})

	return result

def get_quorum(time_limit_secs=10, timestamp=None):
	ts = timestamp or time.time()

	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		SELECT count(npm)
		FROM ewallet_nodes;
	'''

	c.execute(query)
	q_result = c.fetchone()
	conn.close()

	total_nodes = int(q_result[0])
	healthy_nodes = get_live_nodes(time_limit_secs=time_limit_secs, timestamp=timestamp)

	return {
		'healthy_nodes': healthy_nodes,
		'num_healthy': len(healthy_nodes),
		'num_all': total_nodes
	}

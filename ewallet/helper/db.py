import sqlite3

from errors import *

def init_db(dbfile):
	globals()['__DBFILE'] = dbfile

	conn = sqlite3.connect(__DBFILE)
	c = conn.cursor()

	query = '''
		CREATE TABLE IF NOT EXISTS ewallet (
			user_id		text,
			name		text,
			balance		text,
			PRIMARY KEY (user_id)
		)
	'''

	c.execute(query)

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
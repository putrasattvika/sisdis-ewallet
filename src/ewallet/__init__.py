from helper import db
from helper import settings

def ewallet_init(db_user, db_name, node_id, debug=False):
	db.init(db_user, db_name)

	settings.set('NODE_ID', node_id)
	settings.set('DEBUG', debug)

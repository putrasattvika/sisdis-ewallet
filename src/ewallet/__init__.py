import msgqueue

from helper import db
from helper import settings
from utils import *
from query import *
from banking import *

def ewallet_init(db_user, db_name, node_id, debug=False):
	db.init(db_user, db_name)

	settings.set('NODE_ID', node_id)
	settings.set('DEBUG', debug)

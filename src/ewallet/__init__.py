from helper import db
from helper import settings
from utils import *
from query import *
from banking import *

def ewallet_init(dbfile, node_id, debug=False):
	db.init_db(dbfile)

	settings.set('NODE_ID', node_id)
	settings.set('DEBUG', debug)

from helper import db
from helper import settings
from utils import *
from query import *
from banking import *

def ewallet_init(dbfile, debug=False):
	db.init_db(dbfile)
	settings.set('DEBUG', debug)

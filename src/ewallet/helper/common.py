from datetime import datetime

def date2str(date):
	return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

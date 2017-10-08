class DBError(Exception):
	"""Raise for generic DB exceptions"""

class DBUserNotFoundError(DBError):
	"""Raise for missing user exceptions"""

class DBUserAlreadyExistsError(DBError):
	"""Raise for user already exists exceptions"""

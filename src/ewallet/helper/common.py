import requests


NODE_LIST_URL = 'http://152.118.31.2/list.php'

def get_node_list():
	try:
		return requests.get(NODE_LIST_URL, timeout=1).json()
	except:
		return [{ "ip": "localhost:5000", "npm": "-1" }]
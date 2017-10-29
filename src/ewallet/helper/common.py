import requests

NODE_LIST_URL = 'http://152.118.31.2/list.php'
DEBUG_NODE_LIST_URL = 'http://172.21.0.1:5000/'

def get_node_list(debug=False):
	try:
		if debug:
			return requests.get(DEBUG_NODE_LIST_URL, timeout=1).json()

		return requests.get(NODE_LIST_URL, timeout=1).json()
	except:
		return [{ "ip": "localhost:10034", "npm": "-1" }]

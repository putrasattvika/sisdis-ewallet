import requests
from datetime import datetime

NODE_LIST_URL = 'http://152.118.31.2/list.php'
DEBUG_NODE_LIST_URL = 'http://172.21.0.1:5000/'
EXCLUSION_FILE_PATH = 'exclude.txt'

try:
	_excluded_ips = open(EXCLUSION_FILE_PATH, 'r').read().split('\n')
except:
	_excluded_ips = []

def get_node_list(debug=False):
	node_list = []

	try:
		if debug:
			node_list = requests.get(DEBUG_NODE_LIST_URL, timeout=1).json()
		else:
			node_list = requests.get(NODE_LIST_URL, timeout=1).json()
	except:
		node_list = [{ "ip": "localhost:10034", "npm": "-1" }]

	filtered_node_list = []
	for node in node_list:
		if node['ip'] not in _excluded_ips:
			filtered_node_list.append(node)

	return filtered_node_list

def date2str(date):
	return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

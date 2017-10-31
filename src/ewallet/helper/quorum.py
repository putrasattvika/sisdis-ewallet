import requests
from multiprocessing.pool import ThreadPool

import codes
import common
import settings
import url_utils

pool = ThreadPool(processes=4)

def parametrized(dec):
	def layer(*args, **kwargs):
		def repl(f):
			return dec(f, *args, **kwargs)
		return repl
	return layer

def is_node_healthy(node):
	url = url_utils.get_url(node['ip'], url_utils.PING)

	try:
		res = requests.post(url, timeout=1).json()

		if res['pong'] == 1:
			return True, node
	except:
		pass

	return False, None

def inquire():
	node_list = common.get_node_list(debug=settings.DEBUG)

	async_results = []
	for node in node_list:
		async_results.append( pool.apply_async(is_node_healthy, (node,)) )

	healthy_nodes = []
	for async in async_results:
		res = async.get()

		if res[0]:
			healthy_nodes.append(res[1])

	return healthy_nodes

@parametrized
def quorum(f, min_nodes, response_func):
	def aux(*xs, **kws):
		healthy_nodes = inquire()

		if len(healthy_nodes) < min_nodes:
			return response_func(codes.QUORUM_NOT_MET)

		return f(healthy_nodes=healthy_nodes, *xs, **kws)

	return aux

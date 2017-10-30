import requests

import codes
import common
import settings
import url_utils

def parametrized(dec):
	def layer(*args, **kwargs):
		def repl(f):
			return dec(f, *args, **kwargs)
		return repl
	return layer

def inquire():
	node_list = common.get_node_list(debug=settings.DEBUG)

	healthy_nodes = []
	for node in node_list:
		url = url_utils.get_url(node['ip'], url_utils.PING)

		try:
			res = requests.post(url, timeout=1).json()

			if res['pong'] == 1:
				healthy_nodes.append(node)
		except:
			pass

	return healthy_nodes

@parametrized
def quorum(f, min_nodes, response_func):
	def aux(*xs, **kws):
		healthy_nodes = inquire()

		if len(healthy_nodes) < min_nodes:
			return response_func(codes.QUORUM_NOT_MET)

		return f(healthy_nodes=healthy_nodes, *xs, **kws)

	return aux

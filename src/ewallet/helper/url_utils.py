GET_BALANCE = 'getSaldo'
GET_TOTAL_BALANCE = 'getTotalSaldo'
PING = 'ping'
REGISTER = 'register'
TRANSFER = 'transfer'

API_PATHS = [
	GET_BALANCE, GET_TOTAL_BALANCE, PING, 
	REGISTER, TRANSFER
]

def get_url(host, api_path, base_path='ewallet'):
	if api_path not in API_PATHS:
		raise ValueError('Invalid API endpoint, {} is not in {}'.format(api_path, API_PATHS))

	if 'http://' != host[:7]:
		host = 'http://' + host

	if host[-1] == '/':
		host = host[:-1]

	return '{}/{}/{}'.format(host, base_path, api_path)
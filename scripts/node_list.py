import json
import subprocess
from flask import Flask

def _exec(cmd):
	process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
	return process.communicate()[0]

app = Flask(__name__)

@app.route("/")
def hello():
	running_containers = _exec('docker ps -aq').split('\n')
	inspect = json.loads(_exec('docker inspect ' + ' '.join(running_containers)))

	nodes = []
	for node in inspect:
		nodes.append({
			'ip': node['NetworkSettings']['Networks']['sisdisewallet_ewallet']['IPAddress'],
			'npm': node['Id'][:12]
		})

	return json.dumps(nodes)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
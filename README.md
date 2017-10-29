# Distributed eWallet System

First project of Distributed System class, Fasilkom UI 2017/2018.

## Instalation
 * Install curl, python2 and PIP, `apt-get install curl python-minimal python-pip`
 * Install PIP requirements, `pip2 install -r requirements.txt`
 * Run the app, `cd src && python2 app.py --host 0.0.0.0 --port 5000`

## eWallet Server
```
python2 app.py --help
usage: app.py [--id ID] [--host HOST] [--port PORT] [--debug] [--help]

optional arguments:
  --id ID, -i ID        node ID, default is 1406527532
  --host HOST, -h HOST  host IP, default is 0.0.0.0
  --port PORT, -p PORT  listening port, default is 10034
  --debug, -d           debug mode, querying local node listing
  --help                print this help message
```

## eWallet Client
```
python2 ewallet-cli.py --help 
usage: ewallet-cli.py [-h]
                      {ping,register,transfer,get-saldo,get-total-saldo} ...

positional arguments:
  {ping,register,transfer,get-saldo,get-total-saldo}

optional arguments:
  -h, --help            show this help message and exit
```
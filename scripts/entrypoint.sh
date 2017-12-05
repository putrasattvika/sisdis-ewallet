#!/bin/bash

# Init self ID
cgroup=$(cat /proc/self/cgroup | head -1 | grep -Poe "/docker/.*")
self_id=${cgroup:8:12}

# Start & Init PostgreSQL
sed 's@  peer@  trust@' -i /etc/postgresql/9.5/main/pg_hba.conf
su - postgres -c "/etc/init.d/postgresql start"
su - postgres -c "createuser ewallet"
su - postgres -c "psql -c 'CREATE DATABASE ewallet WITH OWNER ewallet;'"

# Init data
reg_cmd="python2 ewallet-cli.py -r --docker --id $self_id register $self_id $self_id $self_id"
trf_cmd="python2 ewallet-cli.py -r --docker --id $self_id transfer $self_id $self_id 1000000"

# Start
nohup bash -c "sleep 15 && $reg_cmd && sleep 1 && $trf_cmd" &
python2 app.py --id $self_id --docker

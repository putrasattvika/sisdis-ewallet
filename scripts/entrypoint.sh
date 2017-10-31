#!/bin/bash


cgroup=$(cat /proc/self/cgroup | head -1 | grep -Poe "/docker/.*")
self_id=${cgroup:8:12}

reg_cmd="curl localhost/ewallet/register -H \"Content-Type: application/json\" -d '{ \"user_id\": \"$self_id\", \"nama\":\"$self_id\" }'"
trf_cmd="curl localhost/ewallet/transfer -H \"Content-Type: application/json\" -d '{ \"user_id\": \"$self_id\", \"nilai\":1000000 }'"

nohup bash -c "sleep 5 && $reg_cmd && sleep 1 && $trf_cmd" &
python2 app.py --id $self_id --host 0.0.0.0 --port 80 --debug

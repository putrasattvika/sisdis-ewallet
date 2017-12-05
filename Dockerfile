FROM ubuntu:16.04

RUN sed 's@archive.ubuntu.com@kambing.ui.ac.id@' -i /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y curl python-minimal python-pip
RUN apt-get install -y postgresql

ADD requirements.txt /opt/ewallet/requirements.txt
RUN pip2 install -r /opt/ewallet/requirements.txt

ADD src /opt/ewallet

ADD scripts/entrypoint.sh /opt/ewallet/entrypoint.sh
RUN chmod 0755 /opt/ewallet/entrypoint.sh

WORKDIR /opt/ewallet/
CMD ./entrypoint.sh

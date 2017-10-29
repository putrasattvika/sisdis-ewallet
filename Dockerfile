FROM ubuntu:16.04

RUN sed 's@archive.ubuntu.com@kambing.ui.ac.id@' -i /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y python-minimal python-pip

ADD requirements.txt /opt/ewallet/requirements.txt
RUN pip2 install -r /opt/ewallet/requirements.txt

RUN apt-get update -y
RUN apt-get install -y curl

ADD src /opt/ewallet
RUN rm /opt/ewallet/ewallet.db

ADD scripts/entrypoint.sh /opt/ewallet/entrypoint.sh
RUN chmod 0755 /opt/ewallet/entrypoint.sh

EXPOSE 80
WORKDIR /opt/ewallet/

CMD ./entrypoint.sh

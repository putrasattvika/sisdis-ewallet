FROM ubuntu:16.04

RUN sed 's@archive.ubuntu.com@kambing.ui.ac.id@' -i /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y python-minimal python-pip

ADD requirements.txt /opt/ewallet/requirements.txt
RUN pip2 install -r /opt/ewallet/requirements.txt

ADD src /opt/ewallet
WORKDIR /opt/ewallet/

EXPOSE 80
CMD python2 app.py --host 0.0.0.0 --port 80

FROM python:3.10

COPY requirements.txt .

RUN apt-get -y update
RUN pip install -r requirements.txt

WORKDIR signaling_server
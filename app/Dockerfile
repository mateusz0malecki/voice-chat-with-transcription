FROM python:3.10

RUN apt-get -y update
RUN apt-get install -y libsndfile1 ffmpeg
COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR app
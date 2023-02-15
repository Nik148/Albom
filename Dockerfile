FROM ubuntu:latest

RUN apt-get -y update && \
    apt-get install -y python3

# RUN apt install -y python3-dev

RUN apt-get install -y python3-pip python3-dev libpq-dev
RUN pip install virtualenv
RUN virtualenv venv

COPY requirements.txt requirements.txt

RUN . venv/bin/activate
RUN pip install -r requirements.txt

COPY ./ .

RUN rm -r migrations


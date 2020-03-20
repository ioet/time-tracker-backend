FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements/prod.txt

ENV FLASK_APP time_tracker_api

EXPOSE 5000

CMD ["gunicorn", "-b 0.0.0.0:5000", "run:app"]

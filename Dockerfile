FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements/prod.txt

ENV FLASK_APP time_tracker_api

EXPOSE 5000

CMD ["gunicorn", "-b 0.0.0.0:5000", "run:app"]

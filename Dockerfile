FROM python:3.8-alpine

ARG buildDeps='g++'

WORKDIR /usr/src/app

COPY . .

RUN apk update \
	&& apk add --no-cache $buildDeps gcc unixodbc-dev \
	&& pip3 install --no-cache-dir -r requirements/prod.txt \
	&& apk del $buildDeps \
	&& rm -rfv /root/.cache/pip/* && \
find /usr/local \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rfv '{}' \+

ENV FLASK_APP time_tracker_api

EXPOSE 5000

CMD ["gunicorn", "-b 0.0.0.0:5000", "run:app"]

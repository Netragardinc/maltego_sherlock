FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade gunicorn gevent

WORKDIR /var/www/maltego-trx/sherlock/

ENV SHERLOCK_VERSION 55c680fde1d6eb94e55870e1be6243c88732cea8

RUN curl -sSL https://github.com/sherlock-project/sherlock/archive/$SHERLOCK_VERSION.tar.gz \
	| tar -v -C /var/www/maltego-trx/sherlock/ -xz --strip-components=1
RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /var/www/maltego-trx/

COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN chown -R www-data:www-data /var/www/maltego-trx/

USER www-data

EXPOSE 8080
ENTRYPOINT ["gunicorn"]
# For ssl, add "--bind=0.0.0.0:8443 --certfile=server.crt --keyfile=server.key"
CMD ["--bind=0.0.0.0:8080", "--workers", "3", "-k", "gevent", "project:application"]
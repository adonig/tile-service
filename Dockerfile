FROM python:3.6

EXPOSE 8080/tcp

VOLUME /data

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app/
RUN pip install --no-cache-dir -r requirements/prod.txt

CMD ["python", "-u", "-m", "tile-service"]

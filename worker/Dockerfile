FROM python:3

COPY requirements.txt /app/requirements.txt

VOLUME /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["celery", "-A", "collector", "worker", "--concurrency=20", "--loglevel=info"]

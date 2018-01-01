from celery import Celery

app = Celery(
    broker='amqp://rabbitmq:rabbitmq@rabbit:5672',
    backend='rpc://',
    include=['collector', 'rancher']
)

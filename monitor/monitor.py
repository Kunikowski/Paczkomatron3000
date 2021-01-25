import pika, sys
from pika import credentials
from os import getenv
from dotenv import load_dotenv

load_dotenv()
MQ_HOST = getenv("MQ_HOST")
MQ_VH = getenv("MQ_VH")
MQ_LOGIN = getenv("MQ_LOGIN")
MQ_PASS = getenv("MQ_PASS")
credentials = pika.PlainCredentials(MQ_LOGIN, MQ_PASS)
parameters = pika.ConnectionParameters(MQ_HOST, 5672, MQ_VH, credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='topic')
result = channel.queue_declare(queue='', exclusive=True)
queue  = result.method.queue

channel.queue_bind(exchange='logs', queue=queue, routing_key='*.error')

def callback(ch, method, properties, body):
    print(f'[x] {body.decode()}')
    ch.basic_ack(delivery_tag=method.delivery_tag, multiple=False)

channel.basic_consume(queue=queue, auto_ack=False, on_message_callback=callback)

try:
    print('[*] Waiting for messages. To exit press CRTL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    connection.close()
    print('Interrupted')
    sys.exit(0)
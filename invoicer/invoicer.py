import pika, sys
from pika import credentials
from os import getenv
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()
MQ_HOST = getenv("MQ_HOST")
MQ_VH = getenv("MQ_VH")
MQ_LOGIN = getenv("MQ_LOGIN")
MQ_PASS = getenv("MQ_PASS")
credentials = pika.PlainCredentials(MQ_LOGIN, MQ_PASS)
parameters = pika.ConnectionParameters(MQ_HOST, 5672, MQ_VH, credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='invoices')

def callback(ch, method, properties, body):
    print(f'[x] {body.decode()}')
    data = json.loads(body.decode())
    f = open(f"invoice_{int(datetime.timestamp(datetime.utcnow())*1000000)}.txt", "w")
    f.write(f"Nadawca: {data['sender']}\nOdbiorca: {data['name']}\nSkrytka docelowa: {data['lockerid']}\nRozmiar: {data['size']}")
    f.close()
    ch.basic_ack(delivery_tag=method.delivery_tag, multiple=False)

channel.basic_consume(queue='invoices', auto_ack=False, on_message_callback=callback)

try:
    print('[*] Waiting for messages. To exit press CRTL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    connection.close()
    print('Interrupted')
    sys.exit(0)
import pika
import json

# URL = 'amqps://fzrzebvc:UlR8AmDkg6ecyJ7Eqm21Z6nDtPwQTjkU@moose.rmq.cloudamqp.com/fzrzebvc'
URL = 'localhost'
connection = pika.BlockingConnection(pika.ConnectionParameters(URL))

channel = connection.channel()

channel.queue_declare(queue='digiwallet')


def callback(ch, method, properties, body):
    data = json.loads(body)
    print(data)


channel.basic_consume(queue='digiwallet',
                      auto_ack=True,
                      on_message_callback=callback)

# print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

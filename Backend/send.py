import pika

# Code that gets the user notified that there is a notification.

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='notification')

channel.basic_publish(exchange='',
                      routing_key='notification',
                      body='Notification')
print(" User sent a notification.")

connection.close()

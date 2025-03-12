### *** Acknowledged with the use of Copilot in creating this code. *** ###

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange ='notification.py', exchange_type = 'direct')

channel.queue_declare(queue = 'notification')

channel.queue_bind(exchange = 'notification.py', queue = 'notification', routing_key = 'notification')

channel.basic_publish(exchange = 'notification.py', routing_key = 'notification', body = 'Test Message')

connection.close()

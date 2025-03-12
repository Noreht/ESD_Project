import pika, sys, os

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='notification')

def callback(ch, method, properties, body):
    print(f" User Received Notification: {body}")

channel.basic_consume(queue='notification',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. Press CTRL+C to exit.')
channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
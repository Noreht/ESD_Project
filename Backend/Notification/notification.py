import os
import pika
import threading
import smtplib
import twilio
import twilio.rest
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv
import json

load_dotenv()
ENV = os.environ.get("ENV", "development")

# twilio
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# email
smtp_server = "smtp.gmail.com"
smtp_port = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_sms(to, body):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(body=body, from_=TWILIO_PHONE_NUMBER, to=to)
    print(f"SMS sent to {to}: {body}")


def send_email(to, body):
    print("Send email activated!")
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = body
    msg.attach(MIMEText(body, "plain"))
    print("msg", EMAIL_USER)
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        print("Email:", text)
        server.sendmail(EMAIL_USER, to, text)
        server.quit()
        print(f"Email sent to {to}: {body}")
    except Exception as e:
        print(f"Failed to send email to {to}: {str(e)}")


if ENV == "production":
    RABBITMQ_CONFIGS = [
        {
            "name": "shared_album",
            "host": "",  # INSERT ADDRESS HERE
            "exchange": "SHARED_ALBUM_EXCHANGE",
            "exchange_type": "fanout",  # place exchange type here
            "queue": "SHARED_ALBUM_QUEUE",
            # if non-fanout, input routing key
            "routing_key": "",
        },
        {
            "name": "event_broker",
            "host": "",  # INSERT ADDRESS HERE
            "exchange": "EVENT_BROKER_EXCHANGE",
            "exchange_type": "fanout",
            "queue": "EVENT_BROKER_QUEUE",
            "routing_key": "",
        },
        # awaiting categories and top 5
    ]
else:
    # Development configuration using localhost addresses.
    RABBITMQ_CONFIGS = [
        {
            "name": "shared_album",
            "host": "rabbitmq",
            "exchange": "event_broker_exchange",
            "exchange_type": "fanout",
            "queue": "notifications_queue",
            "routing_key": "",
        },
        {
            "name": "Scenario_1_Notification",
            "host": "rabbitmq",
            "exchange": "video_processing_topic",
            "exchange_type": "topic",
            "queue": "Scenario_1_Notification_Queue",
            "routing_key": "video.processed",
        },
        # awaiting categories and top 5
        #! Notifications 中间 of categories fire n forget to shared_album
        {
            "name": "Scenario2_Categories_To_SharedAlbum",
            "host": "rabbitmq",
            "exchange": "categories_to_sharedalbum_topic",
            "exchange_type": "topic",
            "queue": "categories_to_notifications_queue",
            "routing_key": "cat_firenforget",
        },
    ]


# godbless gpt4-o
def setup_and_consume(config, callback):
    """
    Sets up the connection, channel, exchanges, queues, and starts consuming messages.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config["host"])
        )
        channel = connection.channel()

        # Declare the exchange using the configured exchange type.
        channel.exchange_declare(
            exchange=config["exchange"],
            exchange_type=config["exchange_type"],
            durable=True,
        )

        # Declare the queue.
        channel.queue_declare(queue=config["queue"], durable=True)
        routing_key = config.get("routing_key", "")
        channel.queue_bind(
            exchange=config["exchange"], queue=config["queue"], routing_key=routing_key
        )

        print(
            f"[Notifications] 🟢 Waiting for messages on '{config['name']}' "
            f"from exchange '{config['exchange']}' ({config['exchange_type']}) at {config['host']} "
            f"with routing key '{routing_key}'."
        )

        # Start consuming messages using the provided callback.
        channel.basic_consume(
            queue=config["queue"], on_message_callback=callback, auto_ack=True
        )
        channel.start_consuming()
    except Exception as e:
        print(f"[Notifications] ❌ Error on {config['name']}: {e}")


def callback(ch, method, properties, body):
    print(
        f"Received message from {method.exchange} on queue {method.routing_key}: {body}"
    )
    try:
        #! Theron original code
        # message = json.loads(body)
        # category_result = message.get('categories')
        # root_video = message.get("video_id")
        # email = message.get('email')
        # subscribers = message.get("subscriber_list", "")

        # phone = "88164892"
        # text = f"Hey! Your recently saved video, {root_video}, was saved under {category_result}. Check it out now!"

        # if subscribers != "":
        #     subscribers.append(message.get("input_person"))
        #     for subscriber in subscribers:
        #         await_text = f"Hey! Your friend {message.get('input_person')} just added a new video, {root_video} to your Shared album, {message.get('album_id')}! Check it out soon!"
        #         send_email(subscriber, await_text)
        # if email:
        #     send_email(email, text)
        # if phone:
        #     send_sms(phone, text)

        message = json.loads(body)

        # Common fields
        root_video = message.get("video_id") or message.get("new_vid_id")
        email = message.get(
            "input_person"
        )  #! Hardcoded as of now (Categories need to send a fking email) - Configure in Categories.PY (IDK WHICH ONE)

        print(email)

        album_name = message.get("shared_album_name") or message.get("album_id")
        input_person = message.get("input_person", "Your friend")
        subscribers = message.get("subscriber_list", [])
        new_vid_subcategory = message.get("new_vid_category") or message.get(
            "categories"
        )
        phone = "88164892"  # Demo/test only

        print(f"Email to:{subscribers}")
        if not isinstance(subscribers, list):
            subscribers = []

        # 🎯 DIFFERENT messages based on exchange
        if method.exchange == "event_broker_exchange":
            print("I received from Event Broker")

            # Scenario 1: From Event Broker → notify subscribers (await_text)
            await_text = f"Hey! Your friend {input_person} just added a new video, {root_video} to your Shared album, {album_name}! Check it out soon!"
            subscribers.append(input_person)
            for subscriber in set(subscribers):
                send_email(subscriber, await_text)

        elif method.exchange == "categories_to_sharedalbum_topic":
            print("I received from Categories Fire Forget\n")
            # Scenario 2: From Categories (fire and forget) → Step 10 msg
            msg = (
                f"New video added into {album_name}, under subcategory {new_vid_subcategory} by {input_person}!\n"
                f"Check your updated {album_name} shared album now!"
            )
            if email:
                subscribers.append(input_person)
                for subscriber in set(subscribers):
                    send_email(subscriber, msg)

            send_sms(phone, msg)  # Optional — you can comment this out if not needed

    except Exception as e:
        print(f"Error processing message: {e}")

    print(f"Processed message: {body}")


threads = []
for config in RABBITMQ_CONFIGS:
    thread = threading.Thread(target=setup_and_consume, args=(config, callback))
    thread.start()
    threads.append(thread)


# Add this at the VERY END of the file (last 4 lines)
if __name__ == "__main__":
    print(
        f"[Notifications] 🟢 Listening to: {', '.join([cfg['name'] for cfg in RABBITMQ_CONFIGS])}"
    )
    try:
        threading.Event().wait()  # Block forever with zero CPU usage
    except KeyboardInterrupt:
        print("\n[Notifications] Shutting down...")


# # Acknowledged with the use of Copilot on 15 March for the group project.
# # Copilot was used in helping me to get the correct code to use
# # environment variables.

# import json, pika, os, smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from twilio.rest import Client
# from dotenv import load_dotenv

# # Load environment variables from sensitive_info.env file
# load_dotenv('sensitive_info.env')


# #configuration for shared albums
# AMQP_HOST = os.getenv("RABBITMQ_HOST", "localhost")
# SHARED_ALBUM_EXCHANGE = "shared_album_exchange"  # sent by shared_album (step 9)
# SHARED_ALBUM_QUEUE = "shared_album_queue"  # listen to shared_album

# EVENT_BROKER_EXCHANGE = "event_broker_exchange"  # event_broker (step 3)
# EVENT_BROKER_QUEUE = "notifications_queue"  # listen to event_broker


# # Configure Twilio
# ACCOUNT_SID = os.getenv('ACCOUNT_SID')
# AUTH_TOKEN = os.getenv('AUTH_TOKEN')
# TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# # Configure Email
# smtp_server = 'smtp.gmail.com'
# smtp_port = 587
# EMAIL_USER = os.getenv('EMAIL_USER')
# EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# def send_sms(to, body):
#     client = Client(ACCOUNT_SID, AUTH_TOKEN)
#     message = client.messages.create(
#         body=body,
#         from_=TWILIO_PHONE_NUMBER,
#         to=to
#     )
#     print(f"SMS sent to {to}: {body}")


# def callback(ch, method, properties, body):
#     message = json.loads(body)
#     print(f"User Received Notification: {body}")
#     #identify what is the process being performed
#     if method.routing_key == SHARED_ALBUM_QUEUE:
#         print("📸 Received new video data from []:")
#         print(json.dumps(message, indent=2))

#         print(f"[Notification Microservice] sending to {message['subscriber_list']}")

#         print(
#             f"New video added into Shared Album ({message['shared_album_name']}), under subcategory {message['new_vid_subcategory']}. Check your updated {message['shared_album_name']}"
#         )

#     elif method.routing_key == EVENT_BROKER_QUEUE:
#         print("\n🔔 Received new video data from [Event Broker]:")
#         print(json.dumps(message, indent=2))

#         print(f"[Notification Microservice] sending to {message['subscriber_list']}...")
#         print(
#             f"New video added into Shared Album ({message['album_id']}). Autocategorisation in progress... Please check later for categories into {message['album_id']}"
#         )


#     #send email and sms
#     if 'to' in message and 'body' in message:
#         send_sms(message['to'], message['body'])

#     if 'email' in message and 'body' in message:
#         send_email(message['email'], message['body'])


# def send_email(to, body):
#     msg = MIMEMultipart()
#     msg['From'] = EMAIL_USER
#     msg['To'] = to
#     msg['Subject'] = 'You have received a notification.'
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(EMAIL_USER, EMAIL_PASSWORD)
#         text = msg.as_string()
#         server.sendmail(EMAIL_USER, to, text)
#         server.quit()
#         print(f"Email sent to {to}: {body}")
#     except Exception as e:
#         print(f"Failed to send email to {to}: {str(e)}")


# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()

# channel.exchange_declare(exchange='notifications', exchange_type='direct')
# channel.queue_declare(queue='notification_queue')
# channel.queue_bind(exchange='notifications', queue='notification_queue', routing_key='notification.py')

# channel.basic_consume(queue='notification_queue', on_message_callback=callback, auto_ack=True)

# print('Waiting for messages. To exit, press CTRL+C.')
# channel.start_consuming()

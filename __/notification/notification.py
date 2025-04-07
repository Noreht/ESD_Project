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
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    EMAIL_USER = os.getenv("EMAIL_USER", "joshuangjinhan@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "bhba blvs pjfd mvfn")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to.strip()
    msg["Subject"] = body.replace("\n", "").strip()
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
        print(f"🟢 Email sent to {to}: {body}")

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
        {
            "name": "CatB_to_Shared_album",
            "host": "rabbitmq",
            "exchange": "catb_to_sharedalbum_exchange",
            "exchange_type": "fanout",
            "queue": "catb_to_notifications_queue",
            "routing_key": "",
        },
    ]


# godbless gpt4-o
def setup_and_consume(config, callback):
    """
    Sets up the connection, channel, exchanges, queues, and starts consuming messages.
    """
    try:
        username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
        password = os.getenv("RABBITMQ_PASS", "mypassword")

        credentials = pika.PlainCredentials(username, password)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config["host"], credentials=credentials)
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
            f"[Notifications] 🟢 Waiting for messages on '{config['name']}'"
            f"from exchange '{config['exchange']}' ({config['exchange_type']}) at {config['host']} "
            f"with routing key '{routing_key}'\n"
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
        f"🟢 Received message from [Exchange {method.exchange}] on [Queue {method.routing_key}]: {body}"
    )
    try:

        message = json.loads(body)

        # TODO: for scenario 1 (Send to input_person)
        if method.exchange == "video_processing_topic":
            # message: {"video_id": "Food1.mp4", "categories": "Food", "email": "layfoo@is214.com"}
            print(
                "\n 🟢 Successfully eavesdropped [Vid-Proc] -> [Cat-B] for Scenario1 ... \n"
            )
            video_id = message.get("video_id")
            category = message.get("categories")
            email = message.get("email")
            album_id = message.get("album_id", "")
            subscribers = message.get("subscriber_list", [])

            if email:
                msg = (
                    f"Hey! Your recently saved video, {video_id}, "
                    f"was saved under {category}. "
                    f"Check it out now 👑!"
                )
                send_email(email, msg)

        elif method.exchange == "event_broker_exchange":
            print("🟢 Successfully heard from [Event Broker]... \n")

            # Get data fields from [Event Broker]
            video_id = message.get("video_id") or message.get("new_vid_id")
            album_name = message.get("shared_album_name") or message.get("album_id")
            input_person = message.get("input_person", "Your friend")
            subscribers = message.get("subscriber_list", [])
            category = message.get("category", "")
            phone = "88164892"  # Demo/test onlyno.
            email = message.get("input_person")

            print(f"🟢 Email will be broadcasted to {subscribers} ... \n")

            # Default message for other cases
            email_text = (
                f"Hey! Your friend {input_person} just added a new video, {video_id} to your Shared album, {album_name}! "
                f"Check it out soon! 🎉"
            )

            subscribers.append(input_person)
            for subscriber in set(subscribers):
                send_email(subscriber, email_text)

        elif method.exchange == "catb_to_sharedalbum_exchange":
            print("🟢 Successfully heard from [CatB]... \n")

            # Get data fields from [CatB]
            video_id = message.get("video_id")
            category = message.get("category", "Uncategorized")
            email = message.get("email") or message.get("email_id")
            album_id = message.get("album_id", "")
            subscriber_list = message.get("subscriber_list", [])

            if email:
                email_text = (
                    f"OMG! A new video, {video_id}, has been added under the subcategory '{category}' "
                    f"in the shared album '{album_id}'. Check it out now to get mindblown!!!!! 😍🐳😌"
                )

                for subscriber in set(subscriber_list):
                    send_email(subscriber, email_text)

    except Exception as e:
        print(f"Error processing message: {e}")

    print(f"\n🟢 Processed message: {body}")


threads = []
for config in RABBITMQ_CONFIGS:
    thread = threading.Thread(target=setup_and_consume, args=(config, callback))
    thread.start()
    threads.append(thread)


# Add this at the VERY END of the file (last 4 lines)
if __name__ == "__main__":
    print(
        f"[Notifications] 🟢 Listening to: {', '.join([cfg['name'] for cfg in RABBITMQ_CONFIGS])}\n"
    )
    try:
        threading.Event().wait()  # Block forever with zero CPU usage
    except KeyboardInterrupt:
        print("\n[Notifications] Shutting down...")

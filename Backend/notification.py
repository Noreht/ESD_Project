# Acknowledged with the use of Copilot on 15 March for the group project.
# Copilot was used in helping me to get the correct code to use
# environment variables.

import json, pika, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from sensitive_info.env file
load_dotenv('sensitive_info.env')

# Configure Twilio
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Configure Email
smtp_server = 'smtp.gmail.com'
smtp_port = 587
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_sms(to, body):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to
    )
    print(f"SMS sent to {to}: {body}")

def send_email(to, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to
    msg['Subject'] = 'Notification'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to, text)
        server.quit()
        print(f"Email sent to {to}: {body}")
    except Exception as e:
        print(f"Failed to send email to {to}: {str(e)}")

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"User Received Notification: {body}")

    if 'to' in message and 'body' in message:
        send_sms(message['to'], message['body'])
    
    if 'email' in message and 'body' in message:
        send_email(message['email'], message['body'])

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='notifications', exchange_type='direct')
channel.queue_declare(queue='notification_queue')
channel.queue_bind(exchange='notifications', queue='notification_queue', routing_key='notification.py')

channel.basic_consume(queue='notification_queue', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit, press CTRL+C.')
channel.start_consuming()

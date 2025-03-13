# Code in charge of notifications.

import pika, json, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

# Twilio configuration
account_sid = 'YOUR_ACCOUNT_SID'
auth_token = 'YOUR_AUTH_TOKEN'
twilio_phone_number = 'YOUR_TWILIO_PHONE_NO'

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_user = 'YOUR_EMAIL_ADDRESS'
email_password = 'YOUR_EMAIL_PASSWORD'

def send_sms(to, body):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=to
    )
    print(f"SMS sent to {to}: {body}")

def send_email(to, body):
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to
    msg['Subject'] = 'Notification'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, to, text)
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

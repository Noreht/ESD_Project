import pika, os


amqp_host = os.getenv("RABBITMQ_HOST", "localhost")  # Default to localhost if not set
amqp_port = int(os.getenv("RABBITMQ_PORT", 5672))
username = os.getenv("RABBITMQ_USER", "myuser")  #! (this may be 'guest')
password = os.getenv("RABBITMQ_PASS", "mypassword")

credentials = pika.PlainCredentials(username, password)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=amqp_host, credentials=credentials)
)
print("Connection successful!")
connection.close()
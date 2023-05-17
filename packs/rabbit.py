import pika

# RabbitMQ server credentials
rabbitmq_host = "127.0.0.1"
rabbitmq_port = "5672"
rabbitmq_username = "test"
rabbitmq_password = "test"

# Create connection parameters
credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)

try:
    # Establish connection
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Print success message
    print("Success: Connected to RabbitMQ")

    # Close connection
    connection.close()

except pika.exceptions.AMQPConnectionError:
    # Print error message if connection fails
    print("Error: Failed to connect to RabbitMQ")
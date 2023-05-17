import pika
from st2reactor.sensor.base import Sensor

class iotrabbitmq(Sensor):
    def __init__(self, sensor_service, config):
        super(iotrabbitmq, self).__init__(sensor_service=sensor_service, config=config)
        self._stopped = False

    def setup(self):
        credentials = pika.PlainCredentials(self._config["sensor_config"]['rabbitmq_username'], self._config["sensor_config"]['rabbitmq_password'])
        parameters = pika.ConnectionParameters(self._config["sensor_config"]['rabbitmq_host'], self._config["sensor_config"]['rabbitmq_port'], credentials=credentials)
    
            # Create a connection to RabbitMQ
        self.connection = pika.BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()

        # Declare the exchange and queue
        self.channel.exchange_declare(exchange=self._config["sensor_config"]['rabbitmq_exchange'], exchange_type=self._config["sensor_config"]['rabbitmq_exchange_type'])
        self.channel.queue_declare(queue=self._config["sensor_config"]['rabbitmq_queue'])
        self.channel.queue_bind(queue=self._config["sensor_config"]['rabbitmq_queue'], exchange=self._config["sensor_config"]['rabbitmq_exchange'], routing_key=self._config["sensor_config"]['rabbitmq_routing_key'])

    def run(self):
        # Start consuming messages from the queue
        self.channel.basic_consume(queue=self._config["sensor_config"]['rabbitmq_queue'], on_message_callback=self._process_message, auto_ack=True)
        while not self._stopped:
            self.channel.connection.process_data_events()

    def cleanup(self):
        self._stopped = True
        self.connection.close()

    def _process_message(self, channel, method, properties, body):
        # Process the incoming message
        payload = body.decode('utf-8')
        self.sensor_service.dispatch(trigger=self._config["sensor_config"]['rabbitmq_message'], payload={'message': payload})
        print(f"Received message: {payload}")
        
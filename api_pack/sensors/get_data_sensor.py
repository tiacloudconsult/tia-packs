from st2reactor.sensor.base import Sensor
from rabbitmq import (
    create_rabbitmq_connection,
    declare_rabbitmq_queue,
    consume_rabbitmq_queue,
)


class GetDataSensor(Sensor):
    def __init__(self, sensor_service, config):
        super(GetDataSensor, self).__init__(sensor_service=sensor_service, config=config)
        self._rabbitmq_conn = None

    def setup(self):
        self._rabbitmq_conn = create_rabbitmq_connection(
            host=self.config["host"],
            port=self.config["port"],
            username=self.config["username"],
            password=self.config["password"],
            vhost=self.config["vhost"],
        )

        declare_rabbitmq_queue(
            channel=self._rabbitmq_conn.channel(),
            queue=self.config["routing_key"],
            exchange=self.config["exchange"],
            queue_durable=self.config["queue_durable"],
        )

        self._rabbitmq_conn.drain_events()

    def run(self):
        consume_rabbitmq_queue(
            channel=self._rabbitmq_conn.channel(),
            queue=self.config["routing_key"],
            exchange=self.config["exchange"],
            callback=self._process_message,
        )

    def cleanup(self):
        if self._rabbitmq_conn is not None:
            self._rabbitmq_conn.close()

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

    def _process_message(self, channel, method, properties, body):
        self.sensor_service.dispatch(trigger="myapi.get_data", payload={"data": body.decode()})

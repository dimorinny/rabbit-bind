#!/usr/bin/python
# -*- encoding: utf-8 -*-
import pika


class Client(object):
    def __init__(self, channel, routing_key, method, no_ack):
        self._channel = channel
        self._routing_key = routing_key
        self._method = method
        self._no_ack = no_ack

    def send(self, data=None):
        if data:
            self._channel.basic_publish(exchange='', routing_key=self._routing_key, body=data)

        if not self._no_ack:
            self._channel.basic_ack(delivery_tag=self._method.delivery_tag)


class RabbitBinder(object):
    def __init__(self, host, no_ack=False, durable=False, prefetch_count=0):
        self._no_ack = no_ack
        self._durable = durable
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count)

    def bind(self, input_queue, output_queue, handler):
        self._channel.queue_declare(queue=input_queue, durable=self._durable)
        self._channel.queue_declare(queue=output_queue, durable=self._durable)

        def _handler(ch, method, properties, body):
            client = Client(self._channel, output_queue, method, self._no_ack)
            handler(body.decode('utf-8'), client)

        self._channel.basic_consume(_handler, queue=input_queue, no_ack=self._no_ack)

    def start(self):
        self._channel.start_consuming()

    def close(self):
        self._connection.close()

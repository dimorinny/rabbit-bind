#!/usr/bin/python
# -*- encoding: utf-8 -*-
import pika


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
            result = handler(body.decode('utf-8'))
            if result:
                self._channel.basic_publish(exchange='', routing_key=output_queue, body=result)

            if not self._no_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self._channel.basic_consume(_handler, queue=input_queue, no_ack=self._no_ack)

    def start(self):
        self._channel.start_consuming()

    def close(self):
        self._connection.close()

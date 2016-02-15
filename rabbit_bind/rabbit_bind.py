#!/usr/bin/python
# -*- encoding: utf-8 -*-
import pika


class RabbitBinder(object):
    def __init__(self, host):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self._channel = self._connection.channel()

    def bind(self, input_queue, output_queue, handler):
        self._channel.queue_declare(queue=input_queue)
        self._channel.queue_declare(queue=output_queue)

        def _handler(ch, method, properties, body):
            result = handler(body)
            if result:
                self._channel.basic_publish(exchange='', routing_key=output_queue, body=result)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self._channel.basic_consume(_handler, queue=input_queue)

    def start(self):
        self._channel.start_consuming()

    def close(self):
        self._connection.close()

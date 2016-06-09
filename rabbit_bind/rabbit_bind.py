#!/usr/bin/python
# -*- encoding: utf-8 -*-
import traceback

import pika


class Client(object):
    def __init__(self, channel, output_exchange, output_routing_key, method):
        self._channel = channel
        self._output_routing_key = output_routing_key
        self._output_exchange = output_exchange
        self._method = method

    def send(self, data, routing_key=self._output_routing_key):
        self._channel.basic_publish(exchange=self._output_exchange, routing_key=routing_key, body=data)


class RabbitBinder(object):
    def __init__(self, host, connection_attempts=None, retry_delay=None, no_ack=False, requeue=True, durable=False,
                 prefetch_count=0):
        self._no_ack = no_ack
        self._durable = durable
        self._requeue = requeue
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, connection_attempts=connection_attempts, retry_delay=retry_delay))
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count)

    def bind(self, input_exchange, input_exchange_type, input_queue_name, input_routing_key,
             output_exchange, output_exchange_type, handler, output_routing_key=''):

        self._channel.exchange_declare(exchange=input_exchange,
                                       exchange_type=input_exchange_type,
                                       durable=self._durable)

        self._channel.exchange_declare(exchange=output_exchange,
                                       exchange_type=output_exchange_type,
                                       durable=self._durable)

        self._channel.queue_declare(queue=input_queue_name, durable=self._durable)
        self._channel.queue_bind(queue=input_queue_name, exchange=input_exchange, routing_key=input_routing_key)

        # noinspection PyBroadException
        def _handler(ch, method, properties, body):
            client = Client(self._channel, output_exchange, output_routing_key, method)
            try:
                success = handler(body.decode('utf-8'), client)

                if not self._no_ack:
                    if success:
                        self._channel.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        self._channel.basic_reject(delivery_tag=method.delivery_tag, requeue=self._requeue)
            except Exception:
                traceback.print_exc()
                self._channel.basic_reject(delivery_tag=method.delivery_tag, requeue=self._requeue)

        self._channel.basic_consume(_handler, queue=input_queue_name, no_ack=self._no_ack)

    def start(self):
        self._channel.start_consuming()

    def close(self):
        self._connection.close()

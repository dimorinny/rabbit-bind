#!/usr/bin/python
# -*- encoding: utf-8 -*-
import json

from rabbit_bind import RabbitBinder


def handler(msg, client):
    print(msg)
    msg = json.loads(msg)

    # Do something with data
    msg['Send'] = True

    client.send(json.dumps(msg))
    return False


def main():
    binder = RabbitBinder(host='localhost', requeue=False)

    binder.bind(input_exchange='input_exchange',
                input_exchange_type='direct',
                input_queue_name='input_queue_name',
                input_routing_key='input_routing_key',
                output_exchange='output_exchange',
                output_exchange_type='fanout',
                handler=handler)

    binder.start()
    binder.close()

if __name__ == "__main__":
    main()

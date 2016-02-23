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


def main():
    binder = RabbitBinder(host='localhost')
    binder.bind('news_input_queue', 'news_output_queue', handler)
    binder.start()
    binder.close()

if __name__ == "__main__":
    main()

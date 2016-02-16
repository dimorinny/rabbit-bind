#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import re

from setuptools import setup


def get_version_from_init():
    file = open(os.path.join(os.path.dirname(__file__), 'rabbit_bind', '__init__.py'))

    regexp = re.compile(r".*__version__ = '(.*?)'", re.S)
    version = regexp.match(file.read()).group(1)
    file.close()

    return version


setup(
    name='rabbit_bind',
    license='MIT',
    author='Dmitry Merkurev',
    author_email='didika914@gmail.com',
    version=get_version_from_init(),
    url='https://github.com/dimorinny/rabbit-bind',
    packages=[
        'rabbit_bind'
    ],
    package_dir={'rabbit_bind': 'rabbit_bind'},
    install_requires=[
        'pika'
    ]
)

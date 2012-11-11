# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='email_reply_parser',
    version='0.1.2',
    description='A email parser library, making it easy to extract a signature, reply, or quote block from a text-formatted email.',
    author='Royce Haynes',
    author_email='royce.haynes@gmail.com',
    url='https://github.com/zapier/email-reply-parser',
    license='MIT',
    packages=find_packages(exclude=('tests')),
    test_suite='tests.test_email_message'
)
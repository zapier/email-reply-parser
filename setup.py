# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='email_reply_parser',
    version='0.1.5',
    description='A email parser library, making it easy to extract a signature, reply, or quote block from a text-formatted email.',
    packages=find_packages('email_reply_parser', 'tests'),
    long_description=read('README.md'),
    author='Royce Haynes',
    author_email='royce.haynes@gmail.com',
    url='https://github.com/zapier/email-reply-parser',
    license=read('LICENSE'),
    test_suite='tests.test_email_reply_parser'
)

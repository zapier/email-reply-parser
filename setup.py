# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = {}
execfile("email_reply_parser/version.py", {}, version)

setup(
    name='py-email_reply_parser',
    version=version['VERSION'],
    description='Email reply parser',
    packages=['email_reply_parser'],
    package_data={'email_reply_parser': ['../VERSION']},
    author='Franklyn Tackitt',
    author_email='frank@comanage.com',
    url='https://github.com/DisruptiveLabs/email-reply-parser',
    license='MIT',
    test_suite='test',
    classifiers=[
        'Topic :: Software Development',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ]
)

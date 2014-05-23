# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'email_reply_parser'))
import version

setup(
    name='email_reply_parser',
    version=version.VERSION,
    description='Email reply parser',
    packages=['email_reply_parser'],
    package_data={'email_reply_parser': ['../VERSION']},
    author='Royce Haynes',
    author_email='royce.haynes@gmail.com',
    url='https://github.com/zapier/email-reply-parser',
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

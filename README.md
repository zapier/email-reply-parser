# Email Reply Parser for Python

[![Build Status](https://secure.travis-ci.org/zapier/django-drip.png)](http://travis-ci.org/zapier/email_reply_parser)

## Summary

Email Reply Parser is a port of GitHub's Email Reply Parser library, making it easy to fragment email.

## Installation

Using pip, use command:

pip install email_reply_parser

## Tutorial

How to parse an email message:

Step 1: import package

from email_reply_parser import EmailReplyParser

Step 2: Pass in email message as type String

EmailReplyParser.read(text)



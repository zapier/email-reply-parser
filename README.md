# Email Reply Parser for Python

## Summary

Email Reply Parser is a port of GitHub's Email Reply Parser library, making it easy to fragment email.

[![Build Status](https://secure.travis-ci.org/zapier/email-reply-parser.png?branch=master)](https://travis-ci.org/zapier/email-reply-parser)

## Installation

Using pip, use command:

pip install email_reply_parser

## Tutorial

How to parse an email message:

Step 1: import package

from email_reply_parser import EmailReplyParser

Step 2: Pass in email message as type String

EmailReplyParser.read(text)



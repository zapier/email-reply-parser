# Email Reply Parser for Python

## Summary

Email Reply Parser is a port of GitHub's Email Reply Parser library, making it easy to fragment email.

[![Build Status](https://secure.travis-ci.org/zapier/email-reply-parser.png?branch=master)](https://travis-ci.org/zapier/email-reply-parser)

## Installation

Using pip, use command:

```
pip install email_reply_parser
```

## Tutorial

### How to parse an email message

Step 1: Import email reply parser package

```python
from email_reply_parser import EmailReplyParser
```

Step 2: Provide email message as type String

```python
EmailReplyParser.read(email_message)
```

### How to only retrieve the reply message

Step 1: Import email reply parser package

```python
from email_reply_parser import EmailReplyParser
```

Step 2: Provide email message as type string using parse_reply class method.

```python
EmailReplyParser.parse_reply(email_message)
```



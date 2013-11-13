# Email Reply Parser for Python
A port of GitHub's Email Reply Parser library, by the fine folks at [Zapier](https://zapier.com/).

## Summary

Email Reply Parser makes it easy to grab *only* the last reply to an on-going email thread.

Say you'd like to parse out a user's response to your transaction email messages:

```
Yes that is fine, I will email you in the morning.

On Fri, Nov 16, 2012 at 1:48 PM, Zapier <contact@zapier.com> wrote:

> Our support team just commented on your open Ticket:
> "Hi Royce, can we chat in the morning about your question?"
```

Email clients handle reply formatting differently, making parsing a pain. [We include tests for many cases](https://github.com/zapier/email-reply-parser/tree/master/test/emails). The parsed email:

```
Yes that is fine, I will email you in the morning.
```

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



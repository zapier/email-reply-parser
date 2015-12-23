import re
from regexps import regexps

"""
    email_reply_parser is a python library port of GitHub's Email Reply Parser.

    For more information, visit https://github.com/zapier/email-reply-parser
"""


class EmailReplyParser(object):
    """ Represents a email message that is parsed.
    """

    @staticmethod
    def read(text, locale='en'):
        """ Factory method that splits email into list of fragments

            text - A string email body

            Returns an EmailMessage instance
        """
        return EmailMessage(text, locale).read()

    @staticmethod
    def parse_reply(text, locale='en'):
        """ Provides the reply portion of email.

            text - A string email body

            Returns reply body message
        """
        return EmailReplyParser.read(text).reply


class EmailMessage(object):
    """ An email message represents a parsed email body.
    """

    def __init__(self, text, locale='en'):
        self.fragments = []
        self.fragment = None
        self.text = text.replace('\r\n', '\n')
        self.found_visible = False
        self.regexps = regexps(locale)

    def read(self):
        """ Creates new fragment for each line
            and labels as a signature, quote, or hidden.

            Returns EmailMessage instance
        """

        self.found_visible = False

        is_multi_quote_header = re.search(self.regexps['multi_quote_hdr'], self.text, re.MULTILINE | re.DOTALL)
        if is_multi_quote_header:
            expr = re.compile(self.regexps['multi_quote_hdr'], flags=re.DOTALL)
            self.text = expr.sub(
                is_multi_quote_header.groups()[0].replace('\n', ''),
                self.text)

        self.lines = self.text.split('\n')
        self.lines.reverse()

        for line in self.lines:
            self._scan_line(line)

        self._finish_fragment()

        self.fragments.reverse()

        return self

    @property
    def reply(self):
        """ Captures reply message within email
        """
        reply = []
        for f in self.fragments:
            if not (f.hidden or f.quoted):
                reply.append(f.content)
        return '\n'.join(reply)

    def _scan_line(self, line):
        """ Reviews each line in email message and determines fragment type

            line - a row of text from an email message
        """

        is_quoted = re.match(self.regexps['quoted'], line) is not None
        is_header = re.match(self.regexps['header'], line) is not None

        if self.fragment and len(line.strip()) == 0:
            if re.match(self.regexps['sig'], self.fragment.lines[-1]):
                self.fragment.signature = True
                self._finish_fragment()

        if self.fragment and (((self.fragment.headers == is_header) and (self.fragment.quoted == is_quoted))
            or (self.fragment.quoted and (self.quote_header(line) or len(line.strip()) == 0))):

            self.fragment.lines.append(line)
        else:
            self._finish_fragment()
            self.fragment = Fragment(is_quoted, line, headers=is_header)

    def quote_header(self, line):
        """ Determines whether line is part of a quoted area

            line - a row of the email message

            Returns True or False
        """
        return re.match(self.regexps['quote_hdr'], line[::-1]) != None

    def _finish_fragment(self):
        """ Creates fragment
        """

        if self.fragment:
            self.fragment.finish()
            if self.fragment.headers:
                # Regardless of what's been seen to this point, if we encounter a headers fragment,
                # all the previous fragments should be marked hidden and found_visible set to False.
                self.found_visible = False
                for f in self.fragments:
                    f.hidden = True
            if not self.found_visible:
                if self.fragment.quoted \
                or self.fragment.headers \
                or self.fragment.signature \
                or (len(self.fragment.content.strip()) == 0):

                    self.fragment.hidden = True
                else:
                    self.found_visible = True
            self.fragments.append(self.fragment)
        self.fragment = None


class Fragment(object):
    """ A Fragment is a part of
        an Email Message, labeling each part.
    """

    def __init__(self, quoted, first_line, headers=False):
        self.signature = False
        self.headers = headers
        self.hidden = False
        self.quoted = quoted
        self._content = None
        self.lines = [first_line]

    def finish(self):
        """ Creates block of content with lines
            belonging to fragment.
        """
        self.lines.reverse()
        self._content = '\n'.join(self.lines)
        self.lines = None

    @property
    def content(self):
        return self._content

"""
email_reply_parser is a python library port of GitHub's Email Reply Parser.
For more information, visit https://github.com/zapier/email_reply_parser
"""
import os
import re
import json


class EmailReplyParser(object):
    """ Represents a email message that is parsed.
    """
    def __init__(self, language='en'):
        dir_path = os.path.dirname(__file__)
        with open(dir_path + "/languages_support.json", "r") as read_file:
            self.words_map = json.load(read_file)
        if language in self.words_map:
            self.language = language
        else:
            self.language = 'en'

    def read(self, text):
        """ Factory method that splits email into list of fragments
            text - A string email body
            Returns an EmailMessage instance
        """
        return EmailMessage(text, self.language, self.words_map).read()

    def parse_reply(self, text):
        """ Provides the reply portion of email.
            text - A string email body
            Returns reply body message
        """
        return self.read(text).reply


class EmailMessage(object):
    """ An email message represents a parsed email body.
    """
    def __init__(self, text, language, words_map):
        self.fragments = []
        self.fragment = None
        self.text = text.replace('\r\n', '\n')
        self.found_visible = False
        self.SIG_REGEX = None
        self.QUOTE_HDR_REGEX = None
        self.QUOTED_REGEX = None
        self.HEADER_REGEX = None
        self._MULTI_QUOTE_HDR_REGEX = None
        self.MULTI_QUOTE_HDR_REGEX = None
        self.MULTI_QUOTE_HDR_REGEX_MULTILINE = None
        self.words_map = words_map
        self.language = language
        self.default_language = 'en'
        self.set_regex()

    def default_quoted_header(self):
        self.QUOTED_REGEX = re.compile(r'(>+)')
        self.HEADER_REGEX = re.compile(
            r'^[* ]?(' + self.words_map[self.language]['From'] +
            '|' + self.words_map[self.language]['Sent'] +
            '|' + self.words_map[self.language]['To'] +
            '|' + self.words_map[self.language]['Subject'] +
            ')\s*:\*? .+|.+(mailto:).+'
        )

    def warnings(self):
        self.WARNING_REGEX = re.compile(r'(CAUTION:|Confidentiality Notice:|Please do not reply|This electronic mail|The information contained|This email has been scanned|This message and any associated files|This message is for the recipients|The [cC]ontents are confidential|This communication with its contents) [a-zA-Z0-9:;.,?!()@/\'\" \-]*')

    def nl_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] + '(\w+\s*){1,3})')
        self.QUOTE_HDR_REGEX = re.compile('Op.*schreef.*>:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Op.*Op\s.+?schreef.*>:)(Op\s(.+?)schreef.*>:)'

    def de_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] + '(\w+\s*){1,3})')
        self.QUOTE_HDR_REGEX = re.compile('Am.*schrieb.*>:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Am.*Am\s.+?schrieb.*>:)(Am\s(.+?)schrieb.*>:)'

    def fr_support(self):
        self.SIG_REGEX = re.compile(
            r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] \
            + '(\w+\s*){1,3})|(.*(cordialement|bonne r[ée]ception|salutations|cdlt|cdt|crdt|regards|best regard|'
              'bonne journ[ée]e))',
            re.IGNORECASE
        )
        self.QUOTE_HDR_REGEX = re.compile('Le.*a écrit.*>:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Le.*Le\s.+?a écrit.*>:)(Le\s(.+?)a écrit.*>:)'

    def en_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^Sent from (\w+\s*){1,6})')
        self.QUOTE_HDR_REGEX = re.compile('\s*On.*wrote:$')
        self.QUOTED_REGEX = re.compile(r'(>+)|((&gt;)+)')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!On.*On\s.+?wrote:)(On\s(.+?)wrote:)'

    def fi_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^Lähetetty (\w+\s*){1,3})|(^Hanki Outlook for.*)')
        self.QUOTE_HDR_REGEX = re.compile('(.+?kirjoitti(.+?kello.+?)?:)')
        self.QUOTED_REGEX = re.compile(r'(>+)|((&gt;)+)')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!.+?kirjoitti.+?kirjoitti[a-zA-Z0-9.:;<>()&@ ]*:$)((.+?)kirjoitti[a-zA-Z0-9.:;<>()&@ ]*:$)'

    def set_regex(self):
        if hasattr(self, self.language+"_support"):
            getattr(self, self.language+"_support")()
            self.default_quoted_header()
        else:
            self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^(' + self.words_map[self.language]['Sent from'] + '|' + self.words_map[self.default_language]['Sent from'] + ')(\w+\s*){1,3})')
            self.QUOTE_HDR_REGEX = re.compile('.*' + self.words_map[self.language]['wrote'] + ':$')
            self.default_quoted_header()
            self._MULTI_QUOTE_HDR_REGEX = r'(?!.+?' + self.words_map[self.language]['wrote'] + \
                                          ':)(On\s(.+?)' + self.words_map[self.language]['wrote'] + ':)'
        self.warnings()
        self.MULTI_QUOTE_HDR_REGEX = re.compile(self._MULTI_QUOTE_HDR_REGEX, re.DOTALL | re.MULTILINE)
        self.MULTI_QUOTE_HDR_REGEX_MULTILINE = re.compile(self._MULTI_QUOTE_HDR_REGEX, re.DOTALL)

    def read(self):
        """ Creates new fragment for each line
            and labels as a signature, quote, or hidden.
            Returns EmailMessage instance
        """

        self.found_visible = False
        is_multi_quote_header = self.MULTI_QUOTE_HDR_REGEX_MULTILINE.search(self.text)
        if is_multi_quote_header:
            self.text = self.MULTI_QUOTE_HDR_REGEX.sub(is_multi_quote_header.groups()[0].replace('\n', ''), self.text)

        # Fix any outlook style replies, with the reply immediately above the signature boundary line
        #   See email_2_2.txt for an example
        self.text = re.sub('([^\n])(?=\n ?[_-]{7,})', '\\1\n', self.text, re.MULTILINE)

        self.text = re.sub(self.WARNING_REGEX, '\n', self.text)

        self.lines = self.text.split('\n')
        self.lines.reverse()

        for line in self.lines:
            if line.strip():
                self._scan_line(line.strip())

        self._finish_fragment()
        self.fragments.reverse()

        return self

    @property
    def reply(self):
        """ Captures reply message within email
        """
        reply = []
        for f in self.fragments:
            if not (f.hidden or f.quoted or f.signature):
                reply.append(f.content)
        return '\n'.join(reply)

    def _scan_line(self, line):
        """ Reviews each line in email message and determines fragment type
            line - a row of text from an email message
        """
        is_quote_header = self.QUOTE_HDR_REGEX.match(line) is not None
        is_quoted = self.QUOTED_REGEX.match(line) is not None
        is_header = is_quote_header or self.HEADER_REGEX.match(line) is not None
        if self.fragment and self.SIG_REGEX.match(line.strip()):
            self.fragment.signature = True
            self.fragment.lines.append(line)
            self._finish_fragment()
        elif self.fragment \
                and ((self.fragment.headers == is_header and self.fragment.quoted == is_quoted) or
                         (self.fragment.quoted and (is_quote_header or len(line.strip()) == 0))):
            self.fragment.lines.append(line)
        else:
            self._finish_fragment()
            self.fragment = Fragment(is_quoted, line, headers=is_header)

    def quote_header(self, line):
        """ Determines whether line is part of a quoted area
            line - a row of the email message
            Returns True or False
        """
        return self.QUOTE_HDR_REGEX.match(line[::-1]) is not None

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
        return self._content.strip()

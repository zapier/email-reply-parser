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
        a = self.read(text).reply
        return a


class EmailMessage(object):
    """ An email message represents a parsed email body.
    """

    def __init__(self, text, language, words_map):
        self.fragments = []
        self.fragment = None
        self.text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.found_visible = False
        self.SIG_REGEX = None
        self.QUOTE_HDR_REGEX = None
        self.QUOTED_REGEX = None
        self.HEADER_REGEX = None
        self._MULTI_QUOTE_HDR_REGEX = None
        self.MULTI_QUOTE_HDR_REGEX = None
        self.MULTI_QUOTE_HDR_REGEX_MULTILINE = None
        self.WARNING_REGEX = None
        self.words_map = words_map
        self.language = language
        self.default_language = 'en'
        self.set_regex()

    def default_quoted_header(self):
        self.QUOTED_REGEX = re.compile(r'(>+)')
        self.HEADER_REGEX = re.compile(
            r'^[* ]*(' + self.words_map[self.language]['From']
            + '|' + self.words_map[self.language]['Sent']
            + '|' + self.words_map[self.language]['To']
            + ')\s*:[\s\n\*]*.*|.+(mailto:).+'
        )

    def warnings(self):
        self.WARNING_REGEX = re.compile(
            r'(CAUTION:|NOTICE:|Confidentiality Notice:|Please do not reply|This electronic mail'
            r'|Disclaimer: This message is intended'
            r'|This message and any attachments are solely'
            r'|This email contains privileged information'
            r'|The information contained|This email has been scanned|This message and any associated files'
            r'|This email and any files transmitted|This message is for the recipients'
            r'|The information provided within this communication'
            r'|This message (including any attachments) is intended'
            r'|The [cC]ontents are confidential|This communication with its contents'
            r'|Please consider the environment before printing this email) [a-zA-Z0-9:;.,?!()@&/\'\"\“\” \-]*'
        )

    def nl_support(self):
        self.SIG_REGEX = re.compile(
            r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] + '(\w+\s*){1,3})'
        )
        self.QUOTE_HDR_REGEX = re.compile('Op.*schreef.*>:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Op.*Op\s.+?schreef.*>:)(Op\s(.+?)schreef.*>:)'

    def de_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] + '(\w+\s*){1,3})')
        self.QUOTE_HDR_REGEX = re.compile('Am.*schrieb.*>:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Am.*Am\s.+?schrieb.*>:)(Am\s(.+?)schrieb.*>:)'

    def fr_support(self):
        self.SIG_REGEX = re.compile(
            r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] \
            + '(\w+\s*){1,3})|(.*(cordialement|bonne r[ée]ception|salutations'
              r'|cdlt|cdt|crdt|regards|best regard|bonne journ[ée]e))',
            re.IGNORECASE
        )
        self.QUOTE_HDR_REGEX = re.compile('Le.*a écrit.*[> ]:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Le.*Le\s.+?a écrit[a-zA-Z0-9.:;<>()&@ -]*:)(Le\s(.+?)a écrit[a-zA-Z0-9.:;<>()&@ -]*:)'

    def en_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^([Ss]ent from|[Gg]et [Oo]utlook)\s(\w+\s*){1,6})')
        self.QUOTE_HDR_REGEX = re.compile('\s*On.*wrote\s*:$')
        self.QUOTED_REGEX = re.compile(r'(>+)|((&gt;)+)')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!On.*On\s.+?wrote\s*:)(On\s(.+?)wrote\s*:)'

    def es_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^Enviado desde (\w+\s*){1,6})')
        self.QUOTE_HDR_REGEX = re.compile('\s*El.*escribió\s*:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!El.*El\s.+?escribió\s*:)(El\s(.+?)escribió\s*:)'

    def ja_support(self):
        self.SIG_REGEX = re.compile(r'--|__|-\w')
        self.QUOTE_HDR_REGEX = re.compile(
            r'[0-9]*年[0-9]*月[0-9]*日[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF\u2605-\u2606\u2190-\u2195\u203Ba-zA-Z0-9.:;<>()&@ -]*:?$'
        )
        self.QUOTED_REGEX = re.compile(r'(>+)|((&gt;)+)')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!On.*On\s.+?wrote\s*:)(On\s(.+?)wrote\s*:)'  # Dummy multiline: doesnt work for japanese due to BeautifulSoup insreting new lines before ":" character

    def fi_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^Lähetetty (\w+\s*){1,3})|(^Hanki Outlook for.*)')
        self.QUOTE_HDR_REGEX = re.compile('(.+?kirjoitti(.+?kello.+?)?:)')
        self.QUOTED_REGEX = re.compile(r'(>+)|((&gt;)+)')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!.+?kirjoitti.+?kirjoitti[a-zA-Z0-9.:;<>()&@ -]*:$)((.+?)kirjoitti[a-zA-Z0-9.:;<>()&@ -]*:$)'

    def set_regex(self):
        if hasattr(self, self.language + "_support"):
            getattr(self, self.language + "_support")()
            self.default_quoted_header()
        else:
            self.SIG_REGEX = re.compile(
                r'(--|__|-\w)|(^(' + self.words_map[self.language]['Sent from']
                + '|' + self.words_map[self.default_language]['Sent from']
                + ')(\w+\s*){1,3})'
            )
            self.QUOTE_HDR_REGEX = re.compile('.*' + self.words_map[self.language]['wrote'] + '\s?:$')
            self.default_quoted_header()
            self._MULTI_QUOTE_HDR_REGEX = r'(?!.+?' + self.words_map[self.language]['wrote'] \
                                          + '\s*:\s*)(On\s(.+?)' + self.words_map[self.language]['wrote'] + ':)'
        self.warnings()
        self.FOLLOW_UP_HDR_REGEX = re.compile(r'(?<!^)This is a follow-up to your previous request.*', re.DOTALL)
        self.MULTI_QUOTE_HDR_REGEX = re.compile(self._MULTI_QUOTE_HDR_REGEX, re.DOTALL | re.MULTILINE)
        self.MULTI_QUOTE_HDR_REGEX_MULTILINE = re.compile(self._MULTI_QUOTE_HDR_REGEX, re.DOTALL)

    def read(self):
        """ Creates new fragment for each line
            and labels as a signature, quote, or hidden.
            Returns EmailMessage instance
        """
        self.text = self.text.strip()
        self.found_visible = False
        is_multi_quote_header = self.MULTI_QUOTE_HDR_REGEX_MULTILINE.search(self.text)
        if is_multi_quote_header:
            self.text = self.MULTI_QUOTE_HDR_REGEX.sub(is_multi_quote_header.groups()[0].replace('\n', ''), self.text)
        self.text = self.FOLLOW_UP_HDR_REGEX.sub('', self.text)
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

        if self.fragment and self.SIG_REGEX.match(self.fragment.lines[-1].strip()):
            self.fragment.signature = True
            self._finish_fragment()
        if self.fragment \
                and ((self.fragment.headers == is_header and self.fragment.quoted == is_quoted) or
                     (self.fragment.quoted and (is_quote_header or len(line.strip()) == 0))):
            self.fragment.lines.append(line)
        else:
            self._finish_fragment()
            self.fragment = Fragment(is_quoted, line, headers=is_header)

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

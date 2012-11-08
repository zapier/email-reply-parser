import re

"""
    Email Reply Parser description
"""


class EmailReplyParser():
    """
    """

    @staticmethod
    def read(text):
        """ Factory method that splits email into list of fragments

            text - A string email body

            Returns an EmailMessage instance
        """
        return EmailMessage(text).read()

    @staticmethod
    def parse_reply(text):
        pass


class EmailMessage():
    """ An email message represents a parsed email body string.
    """

    SIG_REGEX = '(--|__|\w-$)|(^(\w+\s*){1,3} #{"Sent from my".reverse})'

    def __init__(self, text):
        self.fragments = []
        self.fragment = None
        self.text = text

    def read(self):
        """ Creates new fragment for each line
            and labels as a signature, quote, or hidden.
        """

        self.found_visible = False

        self.text = self.text.replace('\r\n', '\n')

        if re.match('^(On\s(.+)wrote:)', self.text):
            self.text = self.text.rstrip('\n')

        self.lines = self.text.split('\n')
        self.lines.reverse()

        for line in self.lines:
            self._scan_line(line)

        self._finish_fragment()

        for f in self.fragments:
            print "================== begin fragment =================="
            print f.content
            print "================== end fragment =================="

        return self

    def _scan_line(self, line):

        line.strip('\n')

        if re.match(self.SIG_REGEX, line):
            line.lstrip()

        is_quoted = re.match('(>+)', line) != None

        if self.fragment and len(line.strip()) == 0:
            if re.match(self.SIG_REGEX, self.fragment.lines[-1]):
                self.fragment.signature = True
                self._finish_fragment()

        if self.fragment and ((self.fragment.quoted == is_quoted)
            or (self.fragment.quoted and (self.quote_header(line) or len(line.strip()) == 0))):
            self.fragment.lines.append(line)
        else:
            self._finish_fragment()
            self.fragment = Fragment(is_quoted, line)

    def quote_header(self, line):
        return re.match('^:etorw.*nO', line) != None

    def _finish_fragment(self):
        if self.fragment:
            self.fragment.finish()
            if not self.found_visible:
                if self.fragment.quoted or self.fragment.signature or not self.fragment.content:
                    self.fragment.hidden = True
                else:
                    self.found_visible = True
            self.fragments.append(self.fragment)
        self.fragment = None


class Fragment():
    """
    """

    def __init__(self, quoted, first_line):
        self.signature = False
        self.hidden = False
        self.quoted = quoted
        self.content = None
        self.lines = [first_line]

    def finish(self):
        self.content = '\n'.join(self.lines)
        self.lines = None

    @property
    def content(self):
        return self.content

    def inspect(self):
        pass

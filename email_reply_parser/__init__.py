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

    def find_contacts(self, text):
        """Provides a list of From To emails and the dates of these emails"""
        contacts_dict = EmailContacts(text, self.language, self.words_map).contacts()
        return contacts_dict


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
            + ')\s*:[\s\n\*]*.*'
        )

    def warnings(self):
        dot = '\u200b'
        single_space = f'[ {dot}\xA0\t]'
        space = f'[,()]?{single_space}{{0,3}}[\n\r]?{single_space}{{0,3}}[,()]?'
        sentence_start = f'(?:[\n\r.!?]|^){single_space}{{0,3}}'
        confidential_variations = f'(privileged|confidential|private|sensitive|{space}(/|and|or|and{space}/{space}or|,){space}){{1,3}}'
        message_variations = f'(electronic{space}|e[\-]?mail{space}|message{space}|communication{space}|transmission{space}){{1,3}}'
        self.WARNING_REGEX = re.compile(
            f'(CAUTION:|NOTICE:|Disclaimer:|Warning:|{confidential_variations}{space}Notice:|Please{space}do{space}not{space}reply'
            f'|{confidential_variations}{space}information'
            f'|{sentence_start}(The|This){space}information{space}(provided|transmitted|contained)?{space}(with)?in{space}this{space}{message_variations}'
            f'|{sentence_start}(The|This){space}information{space}(may also be|is){space}legally'
            f'|{sentence_start}(The|This){space}content[s]?{space}of{space}this{space}{message_variations}'
            f'|{sentence_start}(The|This){space}{message_variations}{space}'
            f'(may{space}contain|(and|or|and{space}/{space}or)?{space}(any|all)?{space}(files{space}transmitted|the{space}information{space}(contained|it{space}contains)|attach|associated)'
            f'|[(]?including{space}(any|all)?{space}attachments[)]?|(is|are|contains){space}{confidential_variations}'
            f'|is{space}for{space}the{space}recipients|is{space}intended{space}only|is{space}for{space}the{space}sole{space}user|has{space}been{space}scanned|with{space}its{space}contents'
            f')|{sentence_start}(The|This){space}publication,{space}copying'
            f'|{sentence_start}(The|This){space}sender{space}(cannot{space}guarantee|believes{space}that{space}this{space}{message_variations})'
            f'|{sentence_start}If{space}you{space}have{space}received{space}this{space}{message_variations}{space}in{space}error'
            f'|{sentence_start}The{space}contents{space}are{space}{confidential_variations}'
            f'|{sentence_start}(Under|According to){space}(the)?{space}(General{space}Data{space}Protection{space}Regulation|GDPR)'
            f'|{sentence_start}Click{space}here{space}to'
            f'|{sentence_start}Copyright{space}'
            f'|{sentence_start}Was{space}this{space}email{space}helpful\?'
            f'|{sentence_start}For{space}Your{space}Information:'
            f'|{sentence_start}Emails{space}are{space}not{space}secure'
            f'|{sentence_start}To make{space}sure{space}you{space}continue{space}to{space}receive'
            f'|{sentence_start}Please{space}choose{space}one{space}of{space}the{space}options{space}below'
            f'|{sentence_start}Please{space}consider{space}the{space}environment{space}before{space}printing{space}this{space}{message_variations}'
            f'|{sentence_start}This{space}e-mail{space}and{space}any{space}attachments{space}are{space}confidential'
            f')[a-zA-Z0-9:;.,?!<>()@&/\'\"\“\” {dot}\xA0\t\-]*',
            re.IGNORECASE
        )

    def nl_support(self):
        self.SIG_REGEX = re.compile(
            r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] + '(\w+\s*){1,3})'
        )
        self.QUOTE_HDR_REGEX = re.compile('Op.*schreef.*>:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Op.*Op\s.+?schreef.*>:)(Op\s(.+?)schreef.*>:)'

    def de_support(self):
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^' + self.words_map[self.language]['Sent from'] + '(\w+\s*){1,3})')
        self.QUOTE_HDR_REGEX = re.compile('[a-zA-Z]{2,5}.*schrieb.*:$')
        self._MULTI_QUOTE_HDR_REGEX = r'(?!Am.*Am\s.+?schrieb.*:)(Am\s(.+?)schrieb.*:)'

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
        self.SIG_REGEX = re.compile(r'(--|__|-\w)|(^(sent from|get outlook)\s(\w+\s*){1,6})|(Best regards|Kind Regards|Thanks,|Thank you,|Best,|All the best|regards,)', flags=re.IGNORECASE)
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


class EmailContacts(EmailMessage):

    def contacts(self):
        self.text = self.text.strip()
        HEADER_BLOCK = re.compile(
            r'('
            + '[>* ]*' + self.words_map[self.language]['From'] + '[ ]*:(.*)\n'
            + '[>* ]*(?:' + self.words_map[self.language]['Sent'] + '|Date)[ ]*:(.*)\n'
            + '[>* ]*' + self.words_map[self.language]['To'] + '[ ]*:(.*)\n'
            + ')'
        )
        EMAIL = re.compile(r'([a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,5})')
        headers = HEADER_BLOCK.findall(self.text)
        json = []
        for header in headers:
            contact = {'from': '', 'to': '', 'date': ''}
            from_email = EMAIL.search(header[1])
            if from_email:
                contact['from'] = from_email.groups()[0]
            contact['date'] = header[2]
            to_email = EMAIL.search(header[3])
            if to_email:
                contact['to'] = to_email.groups()[0]
            json.append(contact)
        return json


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

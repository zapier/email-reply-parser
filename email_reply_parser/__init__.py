"""
    email_reply_parser is a python library port of GitHub's Email Reply Parser.

    For more information, visit https://github.com/zapier/email-reply-parser
"""

import re
from typing import Optional, List
import unidecode


class EmailReplyParser(object):
    """ Represents an email message that is parsed.
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
        """ Provides the reply portion of email.

            text - A string email body

            Returns reply body message
        """
        return EmailReplyParser.read(text).reply

    @staticmethod
    def cut_off_at_signature(body: str, include: Optional[bool] = True, word_limit: Optional[int] = 100):
        """
        Remove the signature section from an email, and use the email Reply Parser to try to remove any
        "thread" content.
        Languages supported: English, French, German, Romanian, Spanish, Italian.
        :param body: The email string to be parsed and cleaned.
        :param include: Boolean variable that determines whether an email is cut-off before the signature or
        after. Default True.
        :param word_limit: If we set the word-limit to None the string will not be split and line breaks will
        be retained. If a word-limit is set, the email will be cut-off after that limit if a signature is not
        found before that point. Default = 100.
        """
        parsed_email = EmailReplyParser.parse_reply(body)
        cleaned_email = EmailMessage.clean_email_content(parsed_email, include, word_limit)
        return cleaned_email.strip()


class EmailMessage(object):
    """ An email message represents a parsed email body.
        The regexes cover English, Italian, Swedish, Finnish, Danish, German, Portuguese, Polish, French to date.
    """
    SENT_FROM_DEVICE_REGEX = re.compile(
        r"(^--|^__|^\* \* \*)"
        r"|(^Sent from .{,50}$)"  # English
        r"|(^Sent using the mobile mail app)"  # English
        r"|(^Get Outlook for .{,50}$)"  # English
        r"|(^Sendt fra .{,50}$)"  # Danish
        r"|(^Verstuurd vanaf.{,50}$)"  # Dutch
        r"|(^Verzonden vanuit .{,50}$)"  # Dutch
        r"|(^Hanki .{,50}$)"  # Finnish
        r"|(^Lahetetty .{,50}$)"  # Finnish
        r"|(^Envoye de .{,50}$)"  # French
        r"|(^Envoye depuis .{,50}$)"  # French
        r"|(^Envoye a partir .{,50}$)"  # French
        r"|(^Gesendet mit.{,50}$)"  # German
        r"|(^Gesendet von.{,50}$)"  # German
        r"|(^Estale apo .{,50}$)"  # Greek
        r"|(.{0,50} kuldve$)"  # Hungarian
        r"|(^Inviato da .{,50}$)"  # Italian
        r"|(^Inviato dal .{,50}$)"  # Italian
        r"|(^Wyslane z .{,50}$)"  # Polish
        r"|(^Wysłane z .{,50}$)"  # Polish
        r"|(^Enviado de .{,50}$)"  # Portuguese
        r"|(^Enviado desde .{,50}$)"  # Portuguese
        r"|(^Enviado do .{,50}$)"  # Portuguese
        r"|(^Enviado a partir .{,50}$)"  # Portuguese
        r"|(^Obter o Outlook .{,50}$)"  # Portuguese
        r"|(^Obtener Outlook .{,50}$)"  # Spanish
        r"|(^Trimis de pe .{,50}$)"  # Romanian
        r"|(^Skickat från .{,50}$)"  # Swedish
        r"|(^Skickat fran .{,50}$)"  # Swedish
        r"|(^Στάλθηκε από .{,50}$)", # Greek
        flags=re.MULTILINE
    )

    QUOTE_HDR_REGEX = re.compile(
        r"On.*wrote(.*?):$"  # English
        r"|Il.*ha(.*?)$"  # Italian - in italian the phrase is "ha scritto" but sometimes "scritto" is put on a new line so we won't put the colon at the end
        r"|mån.*skrev(.*?):$"  # Swedish
        r"|man.*skrev(.*?):$"  # Swedish
        r"|tis.*skrev(.*?):$"  # Norwegian
        r"|tors.*skrev(.*?):$"  # Norwegian
        r"|ons.*skrev(.*?):$"  # Norwegian
        r"|Am.*schrieb(.*?):$"  # German
        r"|Von.*gesendet(.*?)"  # German
        r"|ma.*kirjoitti(.*?):$"  # Finnish
        r"|ti.*kirjoitti(.*?):$"  # Finnish
        r"|pe.*kirjoitti(.*?):$"  # Finnish
        r"|ke.*kirjoitti(.*?):$"  # Finnish
        r"|Den.*skrev(.*?):$"  # Danish
        r"|fre.*skrev(.*?):$"  # Danish
        r"|tir.*skrev(.*?):$"  # Danish
        r"|Op.*schreef(.*?):$"  # Dutch
        r"|Op.*geschreven(.*?):$"  # Dutch
        r"|No dia.*escreveu(.*?):$"  # Portuguese
        r"|A.*escreveu(.*?):$"  # Portuguese
        r"|Le.*ecrit(.*?):$"  # French
        r"|El.*escribio(.*?):$"  # Spanish
        r"|El.*escribió(.*?):$"  # Spanish
        r"|En.*escribio(.*?):$"  # Spanish
        r"|En.*escribió(.*?):$"  # Spanish
        r"|Dna.*napisal\(a\)(.*?):$"  # Slovak
        r"|po.*napisal\(a\)(.*?):$"  # Slovak
        r"|Dnia.*napisal\(a\)(.*?):$"  # Polish
        r"|Dnia.*napisał\(a\)(.*?):$"  # Polish
        r"|Στις.*έγραψε(.*?):$"  # Greek
    )

    QUOTED_REGEX = re.compile(r"(>+)")
    HEADER_REGEX = re.compile(
        r"(^(\*+)?.|^(\*)?)(From|Sent|To|Subject"  # English - Need ^(\*+)?. to catch any number of asterisks before
                                                   # the matching word and ^(\*)? to catch for no asterisks 
        r"|Da|A|Data|Oggetto|Inviato"  # Italian
        r"|Från|Datum|Till|Ämne|Skickat"  # Swedish
        r"|Fran|Datum|Till|Amne|Skickat"  # Swedish
        r"|Von|Gesendet|An|Betreff|Datum"  # German
        r"|Lähettäjä|Päiväys|Vastaanottaja|Aihe|Lähetetty"  # Finnish
        r"|Lahettaja|Paivays|Vastaanottaja|Aihe|Lähetetty"  # Finnish
        r"|Fra|Sendt|Til|Emne|Dato"  # Danish
        r"|Obtenir|Telechargez|Envoye|De"  # French
        r"|Από το|Αποστολή|Προς|Θέμα"  # Greek
        r"|De la|Început|La|Subiect"  # Romanian
        r"|De|Enviado|A|Asunto"  # Spanish
        r"|De|Enviado|Para|Assunto|Data):\*?"  # Portuguese
    )
    _MULTI_QUOTE_HDR_REGEX = (
        r"(On (.{,120})\n?(.{,50})?wrote(\s+)?:"  # English
        r"|Il (.{,120})\n?(.{,50})?ha(\s+)?:"  # Italian
        r"|Il (.{,120})\n?(.{,50})?ha(\s+)?scritto:"  # Italian
        r"|mån (.{,120})\n?(.{,50})?skrev(\s+)?:"  # Swedish
        r"|man (.{,120})\n?(.{,50})?skrev(\s+):"  # Swedish
        r"|tis (.{,120})\n?(.{,50})?skrev(\s+):"  # Norwegian
        r"|tors (.{,120})\n?(.{,50})?skrev(\s+):"  # Norwegian
        r"|ons (.{,120})\n?(.{,50})?skrev(\s+):"  # Norwegian
        r"|Am (.{,120})\n?(.{,50})?schrieb(\s+)?::"  # German
        r"|ma (.{,120})\n?(.{,50})?kirjoitti(\s+)?:"  # Finnish
        r"|ti (.{,120})\n?(.{,50})?kirjoitti(\s+)?:"  # Finnish
        r"|pe (.{,120})\n?(.{,50})?kirjoitti(\s+)?:"  # Finnish
        r"|ke (.{,120})\n?(.{,50})?kirjoitti(\s+)?:"  # Finnish
        r"|fre (.{,120})\n?(.{,50})?skrev(\s+)?:"  # Danish
        r"|Den (.{,120})\n?(.{,50})?skrev(\s+)?:"  # Danish
        r"|tir (.{,120})\n?(.{,50})?skrev(\s+)?:"  # Danish
        r"|Op (.{,120})\n?(.{,50})?schreef(\s+)?:"  # Dutch
        r"|Op (.{,120})\n?(.{,50})?geschreven(\s+)?:"  # Dutch
        r"|A (.{,120})\n?(.{,50})?escreveu(\s+)?:"  # Portuguese
        r"|No dia (.{,120})\n?(.{,50})?escreveu(\s+)?:"  # Portuguese
        r"|El (.{,120})\n?(.{,50})?escribio(\s+)?:"  # Spanish
        r"|El (.{,120})\n?(.{,50})?escribió(\s+)?:"  # Spanish
        r"|Le (.{,120})\n?(.{,50})?ecrit(\s+)?:"  # French
        r"|Le (.{,120})\n?(.{,50})?écrit(\s+)?:"  # French
        r"|Dna (.{,120})\n?(.{,50})?napisala\(a\)(\s+)?:"  # Slovak
        r"|po (.{,120})\n?(.{,50})?napisal\(a\)(\s+)?:"  # Slovak
        r"|Dnia (.{,120})\n?(.{,50})?napisal\(a\)(\s+)?:" # Polish
        r"|Dnia (.{,120})\n?(.{,50})?napisał\(a\)(\s+)?:" # Polish
        r"|W dniu (.{,120})\n?(.{,50})?napisal(\s+)?:" # Polish
        r"|W dniu (.{,120})\n?(.{,50})?napisał(\s+)?:" # Polish
        r"|Wiadomość napisana (.{,120})\n?(.{,50})?o godz" # Polish
        r"|Wiadomosc napisana (.{,120})\n?(.{,50})?o godz" # Polish
        r"|Temat: (.{,120})\n?(.{,50})?Adresat:" # Polish
        r"Στις (.{,120})\n?(.{,50})?έγραψε(\s+)?:"  # Greek
        r")"
    )
    MULTI_QUOTE_HDR_REGEX = re.compile(_MULTI_QUOTE_HDR_REGEX)

    EMAIL_SIGNOFF_REGEX = re.compile(
        r"((regards|kind regards|warm regards|best regards|best wishes|sincerely|best|cheers|"
        r"cordialement|très cordialement|bien cordialement|bien a vous|merci d'avance|d'avance merci|"
        r"Vielen Dank|Vielen Dank und LG|Herzliche Grusse|grussen\s?|grusse\s?|liebe Grusse\s?|"
        r"vielen dank im voraus|Mit freundlichen grussen|"
        r"saluti|Cordiali saluti|Distinti saluti|buona giornata|cordialmente|"
        r"o zi buna|o zi buna va urez|cu respect|cu stima|cu bine|toate cele bune|"
        r"saludos cordiales|atentamente|un saludo)(.{0,20})(,|\n))|"
        r"((thank you|thanks!?|thank you in advance|thanks in advance|merci|danke|"
        r"grazie|grazie mille|multumesc\s?|multumesc anticipat|multumesc frumos|gracias|muchos gracias)(,?!?\n))|"
        r"(Pozdrawiam.?|Z powazaniem|z pozdrowieniami)",
        flags=re.IGNORECASE
    )

    EMAIL_HEADER_WARNINGS = [
        "CAUTION:This message is from an EXTERNAL SENDER - be CAUTIOUS, Do NOT Click any links or Open any attachments if you were not expecting them."
    ]

    def __init__(self, text):
        self.fragments = []
        self.fragment = None
        self.text = text.replace('\r\n', '\n')
        self.found_visible = False

    def read(self):
        """ Creates new fragment for each line
            and labels as a signature, quote, or hidden.

            Returns EmailMessage instance
        """

        self.found_visible = False

        is_multi_quote_header = self.MULTI_QUOTE_HDR_REGEX.search(self.text)
        if is_multi_quote_header:
            self.text = self.text[:is_multi_quote_header.start()]

        # Fix any outlook style replies, with the reply immediately above the signature boundary line
        #   See email_2_2.txt for an example
        self.text = re.sub('([^\n])(?=\n ?[_-]{7,})', '\\1\n', self.text, re.MULTILINE)

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
        is_quote_header = self.QUOTE_HDR_REGEX.match(line) is not None
        is_quoted = self.QUOTED_REGEX.match(line) is not None
        is_header = is_quote_header or self.HEADER_REGEX.match(line) is not None

        if self.fragment and len(line.strip()) == 0:
            if self.SENT_FROM_DEVICE_REGEX.match(self.fragment.lines[-1].strip()):
                self.fragment.signature = True
                self._finish_fragment()

        if self.fragment \
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

    @staticmethod
    def clean_email_content(body, include: Optional[bool], word_limit: Optional[int]):
        """
        Determines if a signature can be found and if so, whether to end the email before or after the signature.
        """
        # Make unidecode copy of body to check against SENT_FROM_DEVICE_REGEX and EMAIL_SIGNOFF_REGEX
        body_clean = unidecode.unidecode(body)

        # Find sign-off or sent from device match for unidecode copy
        signoff_matches = list(EmailMessage.EMAIL_SIGNOFF_REGEX.finditer(body_clean))

        # Note we need to ignore the sent from if it is on the first line of the message
        end_of_first_line_index = body_clean.find("\n")

        # If the signoff match is in the first line of an email, it is likely a mistake (e.g. "Dear Mr. George Best,")
        signoff_matches = [match for match in signoff_matches if match.start() > end_of_first_line_index]


        sent_from_device_matches = []
        if end_of_first_line_index != -1:
            sent_from_device_matches = EmailMessage.SENT_FROM_DEVICE_REGEX.finditer(body_clean)
            sent_from_device_matches = [
                match for match in sent_from_device_matches if match.start() > end_of_first_line_index
            ]

        if include is True:
            # Keep the sign-off
            body = EmailMessage.keep_signoff(body, signoff_matches, sent_from_device_matches, word_limit)

        else:
            # Remove the sign-off
            body = EmailMessage.remove_signoff(body, signoff_matches, sent_from_device_matches, word_limit)

        # Split the body into lines and remove any "Sent from iPhone" lines
        # Use the unidecode copy to check for matches but remove lines from original body
        body = body.strip()
        body_lines = body.split('\n')
        body_lines_unidecode = unidecode.unidecode(body).split('\n')

        # Check if the first line matches and remove
        if EmailMessage.SENT_FROM_DEVICE_REGEX.match(body_lines_unidecode[0]):
            body_lines = body_lines[1:]

        # Check if the final line matches, remove, and re-join lines
        #if SIG_REGEX.match(body_lines_unidecode[-1]):
        if EmailMessage.SENT_FROM_DEVICE_REGEX.match(body_lines_unidecode[-1]):
            body = '\n'.join(body_lines[:-1])
        else:
            body = '\n'.join(body_lines)

        # Finally remove any warning headers from the email
        body = EmailMessage.remove_substrings_from_text(body, EmailMessage.EMAIL_HEADER_WARNINGS)

        return body

    @staticmethod
    def keep_signoff(
            body: str,
            signoff_matches: List[re.Match],
            sent_from_device_matches: List[re.Match],
            word_limit: Optional[int] = None
    ):
        """
        Find where the signature ends and cut-off the email at that point.
        """

        # first handle any sent from iphone stuff
        if len(sent_from_device_matches) > 0:
            sent_from_device_matches_start = [
                match.start() for match in sent_from_device_matches
            ]
            body = body[:sent_from_device_matches_start[0]]

        # Find where sign-off ends
        signoff_matches_end_positions = [
            signoff_match.end() for signoff_match in signoff_matches
        ]

        if len(signoff_matches_end_positions) > 0 and signoff_matches_end_positions[0] < len(body):
            # If a sign-off was found, check for a signature
            end_of_email = body[signoff_matches_end_positions[0]:]

            signature_matches = re.finditer(
                r"((\w+)[\n.])+|\Z",
                end_of_email,
                flags=re.IGNORECASE
            )

            signature_matches_end_positions = [
                signature_match.end() for signature_match in signature_matches
            ]

            if len(signature_matches_end_positions) > 0:
                # If a signature exists, add the two end positions to get the email cut-off point
                email_cutoff = signoff_matches_end_positions[0] + signature_matches_end_positions[0]
                body = body[:email_cutoff]

            else:
                # If no signature found, cut email off after the sign-off
                body = body[:signoff_matches_end_positions[0]]

        else:
            # If no sign-off found, cut-off after word limit
            body = EmailMessage.word_limit_cut_off(body, word_limit)

        return body

    @staticmethod
    def remove_signoff(
            body: str,
            signoff_matches: List[re.Match],
            sent_from_device_matches: List[re.Match],
            word_limit: Optional[int] = None
    ):
        """
        Find where the sign-off starts and cut-off the email at that point.
        """
        # first handle any sent from iphone stuff
        if len(sent_from_device_matches) > 0:
            sent_from_device_matches_start = [
                match.start() for match in sent_from_device_matches
            ]
            body = body[:sent_from_device_matches_start[0]]

        # Find where signature starts
        signoff_matches_start_positions = [
            signoff_match.start() for signoff_match in signoff_matches
        ]

        if len(signoff_matches_start_positions) > 0 and signoff_matches_start_positions[0] < len(body):
            # If a sign-off was found, cut-off email at starting position
            body = body[:signoff_matches_start_positions[0]]

        else:
            # If no sign-off found, cut-off at word limit
            EmailMessage.word_limit_cut_off(body, word_limit)

        return body

    @staticmethod
    def word_limit_cut_off(body, word_limit):
        """
        Cut-off email at word limit.
        """
        if word_limit is not None:
            # if we can't find the sign-off, let's just take the first 100 words
            email_body_list = body.replace("\n", " \n").split(" ")
            newlines_offset = len([word for word in email_body_list if word == " \n"])
            body = " ".join(email_body_list[:word_limit + newlines_offset]).replace(" \n", "\n")

        return body

    @staticmethod
    def remove_substrings_from_text(body: str, substrings: List[str]) -> str:
        """
        Given an email body and a list of substrings to remove (e.g. external email warning), loop through them and
        replace
        """
        for substring in substrings:
            body = re.sub(substring, "", body)

        return body.strip()


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

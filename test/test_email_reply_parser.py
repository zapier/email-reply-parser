import os
import sys
import unittest
import re

import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from email_reply_parser import EmailReplyParser


class EmailMessageTest(unittest.TestCase):
    def test_simple_body(self):
        message = self.get_email('email_1_1')

        self.assertEqual(3, len(message.fragments))
        self.assertEqual(
            [False, True, True],
            [f.signature for f in message.fragments]
        )
        self.assertEqual(
            [False, True, True],
            [f.hidden for f in message.fragments]
        )
        self.assertTrue("folks" in message.fragments[0].content)
        self.assertTrue("riak-users" in message.fragments[2].content)

    def test_reads_bottom_message(self):
        message = self.get_email('email_1_2')

        self.assertEqual(6, len(message.fragments))
        self.assertEqual(
            [False, True, False, True, False, False],
            [f.quoted for f in message.fragments]
        )

        self.assertEqual(
            [False, False, False, False, False, True],
            [f.signature for f in message.fragments]
        )

        self.assertEqual(
            [False, False, False, True, True, True],
            [f.hidden for f in message.fragments]
        )

        self.assertTrue("Hi," in message.fragments[0].content)
        self.assertTrue("On" in message.fragments[1].content)
        self.assertTrue(">" in message.fragments[3].content)
        self.assertTrue("riak-users" in message.fragments[5].content)

    def test_reads_inline_replies(self):
        message = self.get_email('email_1_8')
        self.assertEqual(7, len(message.fragments))

        self.assertEqual(
            [True, False, True, False, True, False, False],
            [f.quoted for f in message.fragments]
        )

        self.assertEqual(
            [False, False, False, False, False, False, True],
            [f.signature for f in message.fragments]
        )

        self.assertEqual(
            [False, False, False, False, True, True, True],
            [f.hidden for f in message.fragments]
        )

    def test_reads_top_post(self):
        message = self.get_email('email_1_3')

        self.assertEqual(5, len(message.fragments))

    def test_multiline_reply_headers(self):
        message = self.get_email('email_1_6')
        self.assertTrue('I get' in message.fragments[0].content)
        self.assertTrue('On' in message.fragments[1].content)

    def test_captures_date_string(self):
        message = self.get_email('email_1_4')

        self.assertTrue('Awesome' in message.fragments[0].content)
        self.assertTrue('On' in message.fragments[1].content)
        self.assertTrue('Loader' in message.fragments[1].content)

    def test_complex_body_with_one_fragment(self):
        message = self.get_email('email_1_5')

        self.assertEqual(1, len(message.fragments))

    def test_verify_reads_signature_correct(self):
        message = self.get_email('correct_sig')
        self.assertEqual(2, len(message.fragments))

        self.assertEqual(
            [False, False],
            [f.quoted for f in message.fragments]
        )

        self.assertEqual(
            [False, True],
            [f.signature for f in message.fragments]
        )

        self.assertEqual(
            [False, True],
            [f.hidden for f in message.fragments]
        )

        self.assertTrue('--' in message.fragments[1].content)

    def test_deals_with_windows_line_endings(self):
        msg = self.get_email('email_1_7')

        self.assertTrue(':+1:' in msg.fragments[0].content)
        self.assertTrue('On' in msg.fragments[1].content)
        self.assertTrue('Steps 0-2' in msg.fragments[1].content)

    def test_reply_is_parsed(self):
        message = self.get_email('email_1_2')
        self.assertTrue("You can list the keys for the bucket" in message.reply)

    def test_reply_from_gmail(self):
        with open('test/emails/email_gmail.txt') as f:
            self.assertEqual('This is a test for inbox replying to a github message.',
                             EmailReplyParser.parse_reply(f.read()))

    def test_parse_out_just_top_for_outlook_reply(self):
        with open('test/emails/email_2_1.txt') as f:
            self.assertEqual("Outlook with a reply", EmailReplyParser.parse_reply(f.read()))

    def test_parse_out_just_top_for_outlook_with_reply_directly_above_line(self):
        with open('test/emails/email_2_2.txt') as f:
            self.assertEqual("Outlook with a reply directly above line", EmailReplyParser.parse_reply(f.read()))

    def test_parse_out_just_top_for_outlook_with_unusual_headers_format(self):
        with open('test/emails/email_2_3.txt') as f:
            self.assertEqual(
                "Outlook with a reply above headers using unusual format",
                EmailReplyParser.parse_reply(f.read()))

    def test_sent_from_iphone(self):
        with open('test/emails/email_iPhone.txt') as email:
            self.assertTrue("Sent from my iPhone" not in EmailReplyParser.parse_reply(email.read()))

    def test_email_one_is_not_on(self):
        with open('test/emails/email_one_is_not_on.txt') as email:
            self.assertTrue(
                "On Oct 1, 2012, at 11:55 PM, Dave Tapley wrote:" not in EmailReplyParser.parse_reply(email.read()))

    def test_partial_quote_header(self):
        message = self.get_email('email_partial_quote_header')
        self.assertTrue("On your remote host you can run:" in message.reply)
        self.assertTrue("telnet 127.0.0.1 52698" in message.reply)
        self.assertTrue("This should connect to TextMate" in message.reply)

    def test_email_headers_no_delimiter(self):
        message = self.get_email('email_headers_no_delimiter')
        self.assertEqual(message.reply.strip(), 'And another reply!')

    def test_multiple_on(self):
        message = self.get_email("greedy_on")
        self.assertTrue(re.match('^On your remote host', message.fragments[0].content))
        self.assertTrue(re.match('^On 9 Jan 2014', message.fragments[1].content))

        self.assertEqual(
            [False, True, False],
            [fragment.quoted for fragment in message.fragments]
        )

        self.assertEqual(
            [False, False, False],
            [fragment.signature for fragment in message.fragments]
        )

        self.assertEqual(
            [False, True, True],
            [fragment.hidden for fragment in message.fragments]
        )

    def test_pathological_emails(self):
        t0 = time.time()
        message = self.get_email("pathological")
        self.assertTrue(time.time() - t0 < 1, "Took too long")

    def test_doesnt_remove_signature_delimiter_in_mid_line(self):
        message = self.get_email('email_sig_delimiter_in_middle_of_line')
        self.assertEqual(1, len(message.fragments))

    def get_email(self, name):
        """ Return EmailMessage instance
        """
        with open('test/emails/%s.txt' % name) as f:
            text = f.read()
        return EmailReplyParser.read(text)

    def test_issue_15(self):              
        message = self.get_email("email_issue_15")
        self.assertEqual('And this is a response to the test response.\nOn function On  wrote:', message.reply)
    
    def test_multi_quater_reg(self):
        test_string='On function On wrote:\nOn Fri, Jan 5, 2018 at 12:39 PM, Adam Taylor <sampleaddress@example.com>\n\
            wrote: > And this is a test response.\n\
            >\n\
            > On Fri, Jan 5, 2018 at 12:34 PM, Adam Taylor <sampleaddress@example.com>\n\
            > wrote:'
        wrong_result='On Fri, Jan 5, 2018 at 12:34 PM, Adam Taylor <sampleaddress@example.com>\n\
            > wrote:'
        right_result='On Fri, Jan 5, 2018 at 12:39 PM, Adam Taylor <sampleaddress@example.com>\n\
            wrote:'
        #the original reg,find the second reply which is at 12:34 PM
        _MULTI_QUOTE_HDR_REGEX =r'(?!On.*On\s.+?wrote:)(On\s(.+?)wrote:)'
        MULTI_QUOTE_HDR_REGEX = re.compile(_MULTI_QUOTE_HDR_REGEX, re.DOTALL | re.MULTILINE)
        is_multi_quote_header = MULTI_QUOTE_HDR_REGEX.search(test_string)
        self.assertEqual(wrong_result,is_multi_quote_header.groups()[0])

        #the new reg,find the first reply and don't get 'On function On wrote:\n'
        NEW_MULTI_QUOTE_HDR_REGEX=re.compile(r'(On\s((?!\sOn\s).)+wrote:)', re.DOTALL | re.MULTILINE)
        self.assertEqual(right_result,NEW_MULTI_QUOTE_HDR_REGEX.search(test_string).groups()[0])
        
if __name__ == '__main__':
    unittest.main()

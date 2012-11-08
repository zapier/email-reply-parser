import unittest
from context import email_reply_parser
from email_reply_parser import EmailReplyParser


class EmailMessageTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_body(self):
        message = self.get_email('email_1_1')

        self.assertEquals(3, len(message.fragments))

    @unittest.skip("")
    def test_multiline_reply_headers(self):
        message = self.get_email('email_1_6')

        self.assertIn('I get', message.read().text)
        self.assertRegexpMatches('^On', str(message.text))

    def get_email(self, name):
        """ Return EmailMessage instance
        """
        text = open('emails/%s.txt' % name).read()
        return EmailReplyParser.read(text)


if __name__ == '__main__':
    unittest.main()

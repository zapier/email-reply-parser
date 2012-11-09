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

        self.assertEquals(2, len(message.fragments))
        self.assertEquals([False, True],
            map(lambda x: x, [f.signature for f in message.fragments]))
        self.assertEquals([False, True],
            map(lambda x: x, [f.hidden for f in message.fragments]))
        self.assertTrue("folks" in message.fragments[0].content)
        self.assertTrue("riak-users" in message.fragments[1].content)

    def test_reads_bottom_message(self):
        message = self.get_email('email_1_2')

        self.assertEquals(6, len(message.fragments))
        self.assertEquals([False, True, False, True, False, False],
            map(lambda x: x, [f.quoted for f in message.fragments]))

        self.assertEquals([False, False, False, False, False, True],
            map(lambda x: x, [f.signature for f in message.fragments]))

        self.assertEquals([False, False, False, True, True, True],
            map(lambda x: x, [f.hidden for f in message.fragments]))

        self.assertTrue("Hi," in message.fragments[0].content)
        self.assertTrue("On" in message.fragments[1].content)
        self.assertTrue(">" in message.fragments[3].content)
        self.assertTrue("riak-users" in message.fragments[5].content)

    def test_reads_top_post(self):
        message = self.get_email('email_1_3')

        for f in message.fragments:
            print '======= begin fragment ======='
            print f.content
            print '======= end fragment ======='

        self.assertEquals(5, len(message.fragments))

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

import os
import sys
import unittest
import time
from email_reply_parser import EmailReplyParser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class EmailMessageTest(unittest.TestCase):
    def test_simple_body(self):
        message = self.get_email('email_1_1')

        self.assertEqual(2, len(message.fragments))
        self.assertEqual(
            [False, True],
            [f.signature for f in message.fragments]
        )
        self.assertEqual(
            [False, True],
            [f.hidden for f in message.fragments]
        )
        self.assertTrue("folks" in message.fragments[0].content)
        self.assertTrue("riak-users" in message.fragments[1].content)

    def test_multiline_reply_headers(self):
        message = self.get_email('email_1_6')
        print(message)
        self.assertTrue('I get' in message.fragments[0].content)
        self.assertTrue('Sent' in message.fragments[1].content)

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

    def test_reply_from_gmail(self):
        with open('emails/email_gmail.txt') as f:
            self.assertEqual('This is a test for inbox replying to a github message.',
                             EmailReplyParser.parse_reply(f.read()))

    def test_parse_out_just_top_for_outlook_reply(self):
        with open('emails/email_2_1.txt') as f:
            self.assertEqual("Outlook with a reply", EmailReplyParser.parse_reply(f.read()))

    def test_parse_out_just_top_for_outlook_with_reply_directly_above_line(self):
        with open('emails/email_2_2.txt') as f:
            self.assertEqual("Outlook with a reply directly above line", EmailReplyParser.parse_reply(f.read()))

    def test_parse_out_just_top_for_outlook_with_unusual_headers_format(self):
        with open('emails/email_2_3.txt') as f:
            self.assertEqual(
                "Outlook with a reply above headers using unusual format",
                EmailReplyParser.parse_reply(f.read()))

    def test_sent_from_iphone(self):
        with open('emails/email_iPhone.txt') as email:
            self.assertTrue("Sent from my iPhone" not in EmailReplyParser.parse_reply(email.read()))

    def test_email_one_is_not_on(self):
        with open('emails/email_one_is_not_on.txt') as email:
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
        with open('emails/%s.txt' % name) as f:
            text = f.read()
        return EmailReplyParser.read(text)

    def test_include_signature_true(self):
        # Test that the cut_off_at_signature function ends an email after the sign-off when include = True
        message_english = self.get_email('email_signature')
        message_german = self.get_email('email_german')
        message_french = self.get_email('email_french')

        body_english = EmailReplyParser.cut_off_at_signature(message_english.text, include=True, word_limit=100)
        body_german = EmailReplyParser.cut_off_at_signature(message_german.text, include=True, word_limit=100)
        body_french = EmailReplyParser.cut_off_at_signature(message_french.text, include=True, word_limit=100)

        assert body_english.endswith('Kind regards,\n\nPerrin Aybara')
        assert body_german.endswith('Mit freundlichen Grüßen,\n\nLukas')
        assert body_french.endswith('Bien à vous,\n\nNicolette Baudelaire')

    def test_include_signature_false(self):
        # Test that the cut_off_at_signature function ends an email before the sign-off when include = False
        message_english = self.get_email('email_signature')
        message_german = self.get_email('email_german')
        message_french = self.get_email('email_french')

        body_english = EmailReplyParser.cut_off_at_signature(message_english.text, include=False, word_limit=100)
        body_german = EmailReplyParser.cut_off_at_signature(message_german.text, include=False, word_limit=100)
        body_french = EmailReplyParser.cut_off_at_signature(message_french.text, include=False, word_limit=100)

        assert body_english.endswith('email cut-off point.')
        assert body_german.endswith('November vornehmen.')
        assert body_french.endswith("s'il vous plaît?")

    def test_word_limit(self):
        # Test that a long email cuts off after the default or given word limit
        message = self.get_email('long_passage')
        body_default_limit = EmailReplyParser.cut_off_at_signature(message.text, word_limit=100)  # Default value
        body_short = EmailReplyParser.cut_off_at_signature(message.text, word_limit=10)  # Less than default
        body_long = EmailReplyParser.cut_off_at_signature(message.text, word_limit=500)  # More than default

        assert body_default_limit.endswith('"HERE IS ONE HUNDRED!"')
        assert body_short.endswith('TEN!')
        assert body_long.endswith('FIVE HUNDRED IS HERE!')

    def test_clean_email_portuguese(self):
        # Test Portuguese regex
        message = self.get_email('email_portuguese')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=False, word_limit=100)
        assert body.endswith("Cumprimentos\nPedro Mota")

    def test_clean_email_french(self):
        # Test Portuguese regex
        message = self.get_email('email_french_accent_sent_on')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=False, word_limit=100)
        assert body == "Bonjour, ca va bien!"

    def test_clean_email_content_no_change(self):
        # Ensure that a short email with no reply and no signature doesn't change
        message = self.get_email('email_one_line')
        clean_content = EmailReplyParser.cut_off_at_signature(body=message.text, word_limit=1000)
        self.assertEqual(message.text, clean_content)

    def test_end_of_email(self):
        # Check that an email that continues after the sign-off (without being a header or reply) cuts off at signature
        message = self.get_email('email_continue_after_signoff')
        body = EmailReplyParser.cut_off_at_signature(message.text)
        assert body.endswith('Tom Bombadil')

    def test_keep_newlines_when_no_signoff(self):
        # Test that when there is no sign-off message detected at the end, the newlines/spacing are not changed
        message = self.get_email('email_no_signature')
        body = EmailReplyParser.cut_off_at_signature(message.text)
        assert body.endswith("Let's see if it works.\n\nK")

    def test_remove_SIG_REGEX_end(self):
        # Test that any "Sent from iPhone" messages are removed at the end of an email
        message_french = self.get_email('email_iphone_french')
        message_portuguese = self.get_email('email_iphone_portuguese')
        message_polish = self.get_email('email_iphone_polish')
        message_finnish = self.get_email('email_iphone_finnish')

        body_french = EmailReplyParser.cut_off_at_signature(message_french.text)
        body_portuguese = EmailReplyParser.cut_off_at_signature(message_portuguese.text)
        body_polish = EmailReplyParser.cut_off_at_signature(message_polish.text)
        body_finnish = EmailReplyParser.cut_off_at_signature(message_finnish.text)

        assert body_french.endswith("Au revoir,\n\nKelsier")
        assert body_portuguese.endswith("Adeus,\n\nOtis")
        assert body_polish.endswith("Do widzenia,\n\nTriss")
        assert body_finnish.endswith("Hyvästi,\n\nTorin")

    def test_remove_SIG_REGEX_start(self):
        # Test that any "Sent from iPhone" messages are removed at the beginning of an email
        message_english = self.get_email('email_iphone_start')
        message_german = self.get_email('email_iphone_start_german')
        body_english = EmailReplyParser.cut_off_at_signature(message_english.text)
        body_german = EmailReplyParser.cut_off_at_signature(message_german.text)
        assert body_english.startswith('Hi,\n\nCase where the')
        assert body_german.startswith('Hallo,\n\nFall, in dem das')


    def test_parse_response_headers(self):
        """
        Tests that we are parsing out email response headers correctly for multiple languages
        """
        message = self.get_email('email_polish_1')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "Ten tekst powinien pojawić się w treści"

        message = self.get_email('email_polish_2')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "Ten tekst powinien pojawić się w treści"

        message = self.get_email('email_polish_3')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "Ten tekst powinien pojawić się w treści"

        message = self.get_email('email_polish_4')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "Ten tekst powinien pojawić się w treści"

        message = self.get_email('email_greek_1')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body.endswith("Από τον Άδη")

        message = self.get_email('email_malformed_thread_header')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)

        assert body.endswith("que cet e-mail est analysé correctement")

        message = self.get_email('email_with_two_headers')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)

        assert body == "This is the main content"

        message = self.get_email('email_portuguese_1')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "This is the main body"

        message = self.get_email('email_portuguese_2')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "Here is the actual email"

        message = self.get_email('email_portuguese_3')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body.startswith("This is a test")
        assert body.endswith("This should be included")

        message = self.get_email('email_romanian_1')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "This is the actual email"

        message = self.get_email('email_german_2')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body == "This is a german email"

    def test_sent_from_device_in_thread(self):
        """
        Tests that if the thread becomes malformed we will be able to parse out the correct part if a sent from device is present
        """
        message = self.get_email("sent_from_device_in_thread")
        body = EmailReplyParser.cut_off_at_signature(message.text)

        assert body == "Yes that would be fine"


    def test_sent_from_device_in_thread_languages(self):
        """
        Tests that if the thread becomes malformed we will be able to parse out the correct part if a sent from device is present
        """
        message_english = self.get_email("sent_from_device_in_thread_english")
        message_hungarian = self.get_email("sent_from_device_in_thread_hungarian")
        message_dutch = self.get_email("sent_from_device_in_thread_dutch")
        message_romanian = self.get_email("sent_from_device_in_thread_romanian")

        body_english = EmailReplyParser.cut_off_at_signature(message_english.text)
        body_hungarian = EmailReplyParser.cut_off_at_signature(message_hungarian.text)
        body_dutch = EmailReplyParser.cut_off_at_signature(message_dutch.text)
        body_romanian = EmailReplyParser.cut_off_at_signature(message_romanian.text)

        assert body_english == "Yes that would be fine"
        assert body_hungarian == "Yes that would be fine"
        assert body_dutch == "Yes that would be fine"
        assert body_romanian == "Yes that would be fine"

    def test_remove_non_alphabetic_signature_patter(self):
        """
        Tests that we we pick up things like --- and  * * * as signatures and ignore bullets
        """

        message_stars_signoff = self.get_email("email_with_stars_signoff")
        body = EmailReplyParser.cut_off_at_signature(message_stars_signoff.text)
        assert body.endswith("Jim")

        message_dash_signoff = self.get_email("email_signature")
        body = EmailReplyParser.cut_off_at_signature(message_dash_signoff.text)
        assert body.endswith("Perrin Aybara")

        message_bullets = self.get_email("email_with_bullets")
        body = EmailReplyParser.cut_off_at_signature(message_bullets.text)
        assert body.endswith("Jane")

    def test_remove_quoted_text(self):
        """Tests that we cut off an email correctly once we see quoted text '>'"""
        message = self.get_email("email_with_quoted_text")
        body = EmailReplyParser.cut_off_at_signature(message.text)
        assert body.endswith("Tony")

    def test_spanish_signoff(self):
        """
        Tests that we're parsing the 'On Jan 31 X wrote:' correctly in Spanish.
        """
        message = self.get_email('spanish_signoff')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body.endswith('Salud')

    def test_remove_header_warnings(self):
        """
        Tests that we remove any warnings about external emails at the top of emails
        """
        message = self.get_email('email_with_header_warning')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body.startswith('Hi,')
        assert body.endswith('Thanks')


    def test_dont_cut_signature_at_start_of_email(self):
        """
        Some e-emails will start with things like "Dear Mr. Best,\n\nHow are you?" these can get parsed out at the end
        of an email unless handled correctly. This test just makes sure that we handle those correctly.
        """
        first_message = self.get_email("george_best")
        second_message = self.get_email("dutch_beste_example")

        body_first_message = EmailReplyParser.cut_off_at_signature(first_message.text)
        body_second_message = EmailReplyParser.cut_off_at_signature(second_message.text)

        assert body_first_message.startswith("Dear George Best,")
        assert body_first_message.endswith("Phil")
        assert body_second_message.startswith("Beste,")
        assert body_second_message.endswith("Timmy")

    def test_french_sign_off(self):
        """
        Tests that we're parsing the 'On Jan 31 X wrote:' correctly in french.
        """

        message = self.get_email('french_signoff')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body.endswith('Il est signalé site innaxecible')

    def test_german_sign_off(self):
        """
        Tests that we're parsing the 'On Jan 31 X wrote:' correctly in german.
        """

        first_message = self.get_email('german_signoff')
        second_message = self.get_email('german_signoff_2')
        body_first_message = EmailReplyParser.cut_off_at_signature(first_message.text, include=True)
        body_second_message = EmailReplyParser.cut_off_at_signature(second_message.text, include=True)
        assert body_first_message.endswith('Mit freundlichen Grüßen')
        assert body_second_message.endswith('Freundliche Grüße')

    def test_orginal_message_sign_off(self):
        """
        Tests that we're parsing the ---- Original Message ---- correctly in german.
        """
        message = self.get_email('original_message_german')
        body = EmailReplyParser.cut_off_at_signature(message.text, include=True)
        assert body.endswith('Mit freundlichen Grüßen')


if __name__ == '__main__':
    unittest.main()

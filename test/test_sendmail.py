import unittest
from unittest.mock import patch, MagicMock
from mailsend import sendmail

class TestSendMail(unittest.TestCase):

    @patch('mailsend.smtplib.SMTP')
    @patch('mailsend.readConf')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Test email content")
    def test_sendmail_success(self, mock_open, mock_readConf, mock_smtp):
        # Setup the mock return values
        mock_readConf.side_effect = lambda section, key: {
            ("mail", "senderMail"): "testsender@example.com",
            ("mail", "smtpPassword"): "testpassword",
            ("mail", "smtpServer"): "smtp.example.com",
            ("mail", "smtpPort"): "587",
            ("mail", "useSSL"): "true",
        }[(section, key)]

        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.return_value = {}

        result = sendmail("receiver@example.com", "Test Subject", "path/to/template")

        # Check that the sendmail function returns 0 on success
        self.assertEqual(result, 0)
        mock_smtp_instance.sendmail.assert_called_once()

    @patch('mailsend.readFile', return_value=None)
    def test_sendmail_fail_to_read_template(self, mock_readFile):
        result = sendmail("receiver@example.com", "Test Subject", "invalid/path/to/template")

        # Expect the function to return 1 since the template couldn't be read
        self.assertEqual(result, 1)

    @patch('mailsend.smtplib.SMTP')
    @patch('mailsend.readConf')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Test email content")
    def test_sendmail_fail_to_send(self, mock_open, mock_readConf, mock_smtp):
        mock_readConf.side_effect = lambda section, key: {
            ("mail", "senderMail"): "testsender@example.com",
            ("mail", "smtpPassword"): "testpassword",
            ("mail", "smtpServer"): "smtp.example.com",
            ("mail", "smtpPort"): "587",
            ("mail", "useSSL"): "true",
        }[(section, key)]

        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.side_effect = Exception("SMTP Error")

        result = sendmail("receiver@example.com", "Test Subject", "path/to/template")

        # Check that the sendmail function returns 1 on failure
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()

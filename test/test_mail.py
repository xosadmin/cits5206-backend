import unittest
from unittest.mock import patch, mock_open
import smtplib
from mailsend import pswdEmailGen, finalpswdEmailGen, sendmail  # Ensure correct import paths

class TestEmailFunctions(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="mock file content")
    @patch("os.path.exists", return_value=True)
    @patch("mailsend.readConf")  # Ensure correct module path for readConf
    def test_pswdEmailGen_success(self, mock_read_conf, mock_exists, mock_file):
        """Test successful password reset email generation"""
        mock_read_conf.return_value = "http://example.com"  # Mock hostname retrieval
        result = pswdEmailGen("testToken", "testuser")

        # Ensure the file write was successful
        mock_file().write.assert_called_once()
        self.assertTrue(result)  # Expecting True since no exceptions should occur

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_finalpswdEmailGen_success(self, mock_exists, mock_file):
        """Test successful final password email generation"""
        result = finalpswdEmailGen("newPassword", "testuser", "testToken")

        # Ensure the file write was successful
        mock_file().write.assert_called_once()
        self.assertTrue(result)  # Expecting True since no exceptions should occur

    @patch("builtins.open", side_effect=Exception("File error"))
    @patch("mailsend.readConf", return_value="mockHostname")  # Mocking readConf
    def test_pswdEmailGen_failure(self, mock_read_conf, mock_file):
        """Test failure of password reset email generation due to file error"""
        result = pswdEmailGen("testToken", "testuser")
        self.assertFalse(result)  # Expecting False due to file write failure


    @patch("builtins.open", side_effect=Exception("File error"))
    def test_finalpswdEmailGen_failure(self, mock_file):
        """Test failure of final password email generation due to file error"""
        result = finalpswdEmailGen("newPassword", "testuser", "testToken")
        self.assertFalse(result)  # Expecting False due to file write failure

    @patch("mailsend.smtplib.SMTP_SSL")  # Mocking SMTP_SSL
    @patch("mailsend.readFile", return_value="Email content")
    @patch("mailsend.readConf")  # Mock readConf
    def test_sendmail_success(self, mock_read_conf, mock_read_file, mock_smtp_ssl):
        """Test successful email sending with SSL"""
        # Mock configuration values
        mock_read_conf.side_effect = ["sender@example.com", "password", "smtp.example.com", "465", "true"]
        mock_smtp_instance = mock_smtp_ssl.return_value

        result = sendmail("receiver@example.com", "Test Subject", "template.html")

        self.assertEqual(result, 0)  # Expecting success
        mock_smtp_instance.login.assert_called_once_with("sender@example.com", "password")
        mock_smtp_instance.sendmail.assert_called_once()



    @patch("mailsend.smtplib.SMTP_SSL")
    @patch("mailsend.readFile", return_value="Email content")
    @patch("mailsend.readConf")  # Mock readConf
    def test_sendmail_failure(self, mock_read_conf, mock_read_file, mock_smtp_ssl):
        """Test email sending failure due to SMTP error"""
        mock_read_conf.side_effect = ["sender@example.com", "password", "smtp.example.com", "465", "true"]
        mock_smtp_instance = mock_smtp_ssl.return_value
        mock_smtp_instance.sendmail.side_effect = smtplib.SMTPException("Failed to send")

        result = sendmail("receiver@example.com", "Test Subject", "template.html")

        self.assertEqual(result, 1)  # Expecting 1 for failure
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.sendmail.assert_called_once()



    @patch("mailsend.smtplib.SMTP_SSL")
    @patch("mailsend.readFile", return_value=None)  # Simulate missing template
    @patch("mailsend.readConf")  # Mock readConf
    def test_sendmail_template_missing(self, mock_read_conf, mock_read_file, mock_smtp_ssl):
        """Test email sending failure due to missing template file"""
        mock_read_conf.side_effect = ["sender@example.com", "password", "smtp.example.com", "465", "true"]

        result = sendmail("receiver@example.com", "Test Subject", "missing_template.html")

        self.assertEqual(result, 3)  # Expecting 3 because the template is missing


if __name__ == "__main__":
    unittest.main()

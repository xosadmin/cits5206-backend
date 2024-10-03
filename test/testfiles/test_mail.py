import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from your_module import pswdEmailGen, finalpswdEmailGen, sendmail  # Replace with actual module name

class TestEmailFunctions(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="mock file content")
    @patch("os.path.exists", return_value=True)
    @patch("your_module.readConf")
    def test_pswdEmailGen_success(self, mock_read_conf, mock_exists, mock_file):
        """Test successful password reset email generation"""
        mock_read_conf.return_value = "http://example.com"
        result = pswdEmailGen("testToken", "testuser")

        mock_file().write.assert_called_once()  # Check that write was called
        self.assertTrue(result)  # Expecting True since no exceptions should occur

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_finalpswdEmailGen_success(self, mock_exists, mock_file):
        """Test successful final password email generation"""
        result = finalpswdEmailGen("newPassword", "testuser", "testToken")

        mock_file().write.assert_called_once()  # Ensure file write occurred
        self.assertTrue(result)  # Expecting True since no exceptions should occur

    @patch("builtins.open", side_effect=Exception("File error"))
    def test_pswdEmailGen_failure(self, mock_file):
        """Test failure of password reset email generation due to file error"""
        result = pswdEmailGen("testToken", "testuser")
        self.assertFalse(result)  # Expecting False due to file write failure

    @patch("builtins.open", side_effect=Exception("File error"))
    def test_finalpswdEmailGen_failure(self, mock_file):
        """Test failure of final password email generation due to file error"""
        result = finalpswdEmailGen("newPassword", "testuser", "testToken")
        self.assertFalse(result)  # Expecting False due to file write failure

    @patch("your_module.smtplib.SMTP_SSL")
    @patch("your_module.readFile", return_value="Email content")
    @patch("your_module.readConf")
    def test_sendmail_success(self, mock_read_conf, mock_read_file, mock_smtp_ssl):
        """Test successful email sending with SSL"""
        mock_read_conf.side_effect = ["sender@example.com", "password", "smtp.example.com", "465", "true"]
        mock_smtp_instance = mock_smtp_ssl.return_value
        mock_smtp_instance.sendmail.return_value = None  # Simulate successful send

        result = sendmail("receiver@example.com", "Test Subject", "template.html")

        self.assertEqual(result, 0)  # Expecting 0 for success
        mock_smtp_instance.login.assert_called_once_with("sender@example.com", "password")
        mock_smtp_instance.sendmail.assert_called_once()

    @patch("your_module.smtplib.SMTP_SSL")
    @patch("your_module.readFile", return_value="Email content")
    @patch("your_module.readConf")
    def test_sendmail_failure(self, mock_read_conf, mock_read_file, mock_smtp_ssl):
        """Test email sending failure due to SMTP error"""
        mock_read_conf.side_effect = ["sender@example.com", "password", "smtp.example.com", "465", "true"]
        mock_smtp_instance = mock_smtp_ssl.return_value
        mock_smtp_instance.sendmail.side_effect = smtplib.SMTPException("Failed to send")

        result = sendmail("receiver@example.com", "Test Subject", "template.html")

        self.assertEqual(result, 1)  # Expecting 1 for failure
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.sendmail.assert_called_once()

    @patch("your_module.smtplib.SMTP_SSL")
    @patch("your_module.readFile", return_value=None)
    @patch("your_module.readConf")
    def test_sendmail_template_missing(self, mock_read_conf, mock_read_file, mock_smtp_ssl):
        """Test email sending failure due to missing template file"""
        mock_read_conf.side_effect = ["sender@example.com", "password", "smtp.example.com", "465", "true"]

        result = sendmail("receiver@example.com", "Test Subject", "missing_template.html")

        self.assertEqual(result, 1)  # Expecting 1 because the template is missing

if __name__ == "__main__":
    unittest.main()

import sys
import os
import unittest

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db  # Import your Flask app and db instance



class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
        self.app = app.test_client()
        with app.app_context():
            db.create_all()  # Create all tables in the in-memory database

    def tearDown(self):
        with app.app_context():
            db.session.remove()  # Clear the session
            db.drop_all()  # Drop all tables

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No specified command.', response.data)

    def test_register_user(self):
        response = self.app.post('/register', data=dict(username='testuser', password='testpass'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Status', response.data)

    def test_login_user(self):
        # First, register a user
        self.app.post('/register', data=dict(username='testuser', password='testpass'))
        
        # Then attempt to log in
        response = self.app.post('/login', data=dict(username='testuser', password='testpass'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Token', response.data)

    def test_invalid_login(self):
        # Attempt to log in with an incorrect username or password
        response = self.app.post('/login', data=dict(username='invaliduser', password='invalidpass'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wrong username or password', response.data)

    def test_add_note_unauthorized(self):
        # Try to add a note without authorization (without a valid token)
        response = self.app.post('/addnote', data=dict(content='Test Note', podid='1'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Unauthenticated', response.data)

    def test_ping(self):
        # Test the /ping route to ensure the service is running
        response = self.app.get('/ping')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PONG', response.data)

if __name__ == "__main__":
    unittest.main()

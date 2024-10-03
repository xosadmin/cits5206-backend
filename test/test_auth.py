import unittest
import uuid
from flask import jsonify
from app import create_app, db
from models.sqlmodel import Users, Tokens
from utils import md5Calc, uuidGen

class TestAuth(unittest.TestCase):
    def setUp(self):
        # Create the Flask application with 'testing' config
        self.app = create_app('testing')

        # Push the application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Initialize the database
        db.create_all()

        # Initialize the test client
        self.client = self.app.test_client()

        # Create a test user
        self.create_test_user()

    def tearDown(self):
        # Clean up the database after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self):
        # Generate a unique test username
        self.test_username = "testuser_" + str(uuid.uuid4())[:8]
        new_user = Users(
            userID=uuidGen(),
            username=self.test_username,
            password=md5Calc("testpassword"),  # Use md5 hashed password
            firstname="Test",
            lastname="User",
            dob="1/1/1970"
        )
        # Add the user to the database and commit the transaction
        db.session.add(new_user)
        db.session.commit()

    def test_login_success(self):
        """Test a successful login scenario."""
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'testpassword'})
        print("Status Code:", response.status_code)
        print("Response JSON:", response.get_json())
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data.get('Status'))
        self.assertIn('Token', data)  # Verify the token is present in the response

    def test_login_failure_invalid_password(self):
        """Test login with an incorrect password."""
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'wrongpassword'})
        print("Status Code:", response.status_code)
        print("Response JSON:", response.get_json())
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data.get('Status'))  # Ensure the login fails

    def test_register_success(self):
        """Test successful user registration."""
        new_username = "newuser_" + str(uuid.uuid4())[:8]
        response = self.client.post('/register', data={'username': new_username, 'password': 'newpassword123'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['Status'])  # Ensure the registration is successful

    def test_register_failure_user_exists(self):
        """Test registration failure when the username already exists."""
        response = self.client.post('/register', data={'username': self.test_username, 'password': 'password123'})
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertFalse(data['Status'])  # Ensure the failure occurs due to duplicate username

    def test_register_failure_long_username(self):
        """Test registration failure when the username is too long."""
        long_username = 'a' * 256  # Exceed the maximum username length
        response = self.client.post('/register', data={'username': long_username, 'password': 'password123'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['Status'])  # Ensure the failure occurs due to invalid username length

    def test_changepass_success(self):
        """Test successful password change."""
        # Log in to get the authentication token
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'testpassword'})
        token = response.get_json().get('Token')

        # Attempt to change the password
        new_password = 'newtestpassword'
        response = self.client.post('/changepass', data={'tokenID': token, 'password': new_password})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['Status'])  # Ensure the password change is successful

    def test_changepass_failure_invalid_token(self):
        """Test password change with an invalid token."""
        response = self.client.post('/changepass', data={'tokenID': 'invalidtoken', 'password': 'newpassword'})
        print("Status Code:", response.status_code)
        print("Response JSON:", response.get_json())
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['Status'])
        self.assertEqual(data['Detailed Info'], 'Invalid or expired token')  # Ensure proper error message is returned

    def test_setuserinfo_success(self):
        """Test setting user info successfully."""
        # Log in to get the authentication token
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'testpassword'})
        token = response.get_json().get('Token')

        # Get the actual user ID from the database
        user = Users.query.filter_by(username=self.test_username).first()

        # Set user info
        response = self.client.post('/setuserinfo', data={
            'userID': user.userID,  # Use userID instead of tokenID
            'firstname': 'NewFirstName',
            'lastname': 'NewLastName',
            'dob': '01/01/1980'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['Status'])  # Ensure user info update is successful

    def test_setuserinfo_failure_missing_data(self):
        """Test setting user info with missing data."""
        # Log in to get the token
        response = self.client.post('/login', data={'username': self.test_username, 'password': 'testpassword'})
        token = response.get_json().get('Token')

        # Test with missing fields
        response = self.client.post('/setuserinfo', data={'userID': '', 'firstname': '', 'lastname': '', 'dob': ''})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['Status'])  # Ensure failure occurs due to missing data

if __name__ == '__main__':
    unittest.main()

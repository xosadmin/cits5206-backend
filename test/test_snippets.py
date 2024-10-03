import unittest
import uuid
from app import create_app, db
from models.sqlmodel import PodCategory, Users, Tokens, Podcasts, Notes
from utils import md5Calc, uuidGen, getTime, readConf

class TestSnippets(unittest.TestCase):
    def setUp(self):
        # Create a Flask application and push the context
        self.app = create_app('testing')  # Ensure 'testing' uses SQLite in-memory
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Set the database to use SQLite in-memory for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize the database
        db.create_all()

        # Initialize the test client
        self.client = self.app.test_client()

        # Create test data
        self.create_test_user()
        self.create_test_category()  # Ensure category is created before creating podcasts
        self.create_test_podcast()  # Make sure categoryID is assigned to the podcast

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_category(self):
        """Create a test category for linking with podcasts."""
        self.test_category_id = uuidGen()  # Generate a unique category ID
        new_category = PodCategory(
            categoryID=self.test_category_id,
            categoryName="Test Category"
        )
        db.session.add(new_category)
        db.session.commit()

    def create_test_user(self):
        """Create a test user and generate a token"""
        self.test_username = "testuser_" + str(uuid.uuid4())[:8]
        new_user = Users(
            userID=uuidGen(),
            username=self.test_username,
            password=md5Calc("testpassword"),
            firstname="Test",
            lastname="User",
            dob="1/1/1970"
        )
        db.session.add(new_user)
        db.session.commit()

        self.test_user = new_user  # Store the created user for later use

        # Generate a valid token for the test user
        self.test_user_token = uuidGen()
        new_token = Tokens(
            tokenID=uuidGen(),
            userID=self.test_user.userID,
            token=self.test_user_token,
            dateIssue=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(new_token)
        db.session.commit()

    def create_test_podcast(self):
        """Create a test podcast for linking with snippets."""
        self.test_podcast_id = uuidGen()
        new_podcast = Podcasts(
            podID=self.test_podcast_id,
            userID=self.test_user.userID,  # Link to the test user
            categoryID=self.test_category_id,  # Make sure categoryID is valid
            podName="Test Podcast",
            podUrl="http://example.com/testpodcast.mp3",
            podDuration=120,
            updateDate=getTime(readConf("systemConfig", "timezone"))
        )
        db.session.add(new_podcast)
        db.session.commit()

    def test_add_snippet_success(self):
        """Test adding a snippet with valid data."""
        response = self.client.post('/addsnippet', data={
            'tokenID': self.test_user_token,  # Use a valid token
            'podID': self.test_podcast_id,    # Use the valid podcast ID
            'content': 'This is a snippet of the podcast',
            'timestamp': '00:01:30'  # Timestamp where the snippet occurs
        })
        self.assertEqual(response.status_code, 201)  # Ensure that the snippet is created successfully
        data = response.get_json()
        self.assertTrue(data['Status'])
        self.assertIn('SnippetID', data)  # Updated key name to match the response


    def test_add_snippet_invalid_token(self):
        """Test adding a snippet with an invalid token."""
        response = self.client.post('/addsnippet', data={
            'tokenID': 'invalidtoken',  # Invalid token
            'podID': self.test_podcast_id,
            'content': 'This is a snippet of the podcast',
            'timestamp': '00:01:30'
        })
        # Check if the response is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)
        
        # Check if the response contains valid JSON with an error message
        data = response.get_json()
        self.assertFalse(data['Status'])
        self.assertIn('Detailed Info', data)
        self.assertEqual(data['Detailed Info'], 'Invalid or expired token')

    def test_get_snippets_success(self):
        """Test retrieving snippets for a podcast."""
        # First, add a snippet
        response = self.client.post('/addsnippet', data={
            'tokenID': self.test_user_token,
            'podID': self.test_podcast_id,
            'content': 'This is a snippet of the podcast',
            'timestamp': '00:01:30'
        })
        self.assertEqual(response.status_code, 201)
        snippet_id = response.get_json().get('snippetID')

        # Now, retrieve snippets for the podcast
        response = self.client.post('/getsnippets', data={
            'tokenID': self.test_user_token,
            'podID': self.test_podcast_id
        })
        # Check if the response is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains valid JSON and Snippets
        data = response.get_json()
        self.assertTrue(data['Status'])
        self.assertTrue(len(data['Snippets']) > 0)
        
        # Check if the first snippet content matches
        self.assertEqual(data['Snippets'][0]['content'], 'This is a snippet of the podcast')

    def test_get_snippets_invalid_token(self):
        """Test retrieving snippets with an invalid token."""
        response = self.client.post('/getsnippets', data={
            'tokenID': 'invalidtoken',  # Invalid token
            'podID': self.test_podcast_id
        })
        # Check if the response is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)
        
        # Check if the response contains valid JSON with an error message
        data = response.get_json()
        self.assertFalse(data['Status'])
        self.assertIn('Detailed Info', data)
        self.assertEqual(data['Detailed Info'], 'Invalid or expired token')

if __name__ == '__main__':
    unittest.main()

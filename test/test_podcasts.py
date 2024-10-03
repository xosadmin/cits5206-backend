import unittest
import uuid
import os
import tempfile
from app import create_app, db
from models.sqlmodel import Users, Tokens, Podcasts, PodCategory
from utils import md5Calc, uuidGen, getTime, readConf

class TestPodcasts(unittest.TestCase):
    def setUp(self):
        # Create Flask application and push context
        self.app = create_app('testing')  # Ensure SQLite is used for testing
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Set the database URI to use SQLite in-memory for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize the database
        db.create_all()

        # Initialize the test client
        self.client = self.app.test_client()

        # Create test data
        self.create_test_user()
        self.create_test_category()

    def tearDown(self):
        # Drop all database tables after each test
        db.session.remove()
        db.drop_all()

        # Clean up the podcasts directory by removing generated mp3 files
        self.clean_up_podcast_files()

        # Pop the application context
        self.app_context.pop()

    def clean_up_podcast_files(self):
        """Delete all MP3 files generated during the test in the static/podcasts/ directory"""
        podcast_directory = 'static/podcasts/'
        if os.path.exists(podcast_directory):
            for filename in os.listdir(podcast_directory):
                if filename.endswith('.mp3'):
                    file_path = os.path.join(podcast_directory, filename)
                    os.remove(file_path)

    def create_test_user(self):
        """Create a test user and generate a token"""
        self.test_username = "testuser_" + str(uuid.uuid4())[:8]
        self.test_user = Users(
            userID=uuidGen(),
            username=self.test_username,
            password=md5Calc("testpassword"),
            firstname="Test",
            lastname="User",
            dob="1/1/1970"
        )
        db.session.add(self.test_user)
        db.session.commit()

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

    def create_test_category(self):
        """Create a test category"""
        self.test_category = PodCategory(
            categoryID=uuidGen(),
            categoryName='Test Category'
        )
        db.session.add(self.test_category)
        db.session.commit()

    def create_dummy_mp3(self):
        """Create a dummy mp3 file for testing purposes"""
        # Create a temporary file to act as an mp3
        dummy_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        dummy_file.write(b"ID3")  # Minimal MP3 header
        dummy_file.flush()
        dummy_file.close()  # Explicitly close the file before returning its name
        return dummy_file.name

    def test_add_podcast_success(self):
        """Test adding a podcast with valid data"""
        dummy_mp3_path = self.create_dummy_mp3()  # Create dummy mp3

        with open(dummy_mp3_path, 'rb') as f:
            response = self.client.post('/addpodcast', data={
                'tokenID': self.test_user_token,
                'podName': 'Test Podcast',
                'categoryID': self.test_category.categoryID,
                'file': f,
            }, content_type='multipart/form-data')

        os.unlink(dummy_mp3_path)  # Clean up the dummy file

        self.assertEqual(response.status_code, 201)

    def test_delete_podcast_invalid_token(self):
        """Test deleting a podcast with an invalid token"""
        response = self.client.post('/deletepodcast', data={
            'tokenID': 'invalidtoken',
            'podID': 'some_pod_id'
        })
        self.assertEqual(response.status_code, 401)  # Expecting 401 due to invalid token

    def test_delete_podcast_success(self):
        """Test deleting a podcast with valid data"""
        # Add a podcast first
        dummy_mp3_path = self.create_dummy_mp3()  # Create dummy mp3

        with open(dummy_mp3_path, 'rb') as f:
            response = self.client.post('/addpodcast', data={
                'tokenID': self.test_user_token,
                'podName': 'Test Podcast',
                'categoryID': self.test_category.categoryID,
                'file': f,
            }, content_type='multipart/form-data')

        self.pod_id = response.get_json().get('PodcastID')
        os.unlink(dummy_mp3_path)  # Clean up the dummy file

        # Now attempt to delete the podcast
        response = self.client.post('/deletepodcast', data={
            'tokenID': self.test_user_token,
            'podID': self.pod_id
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

import os, sys
import unittest
from app import create_app, db
from models.sqlmodel import Library, Users, Podcasts, PodCategory
from utils import readConf, uuidGen, md5Calc, getTime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Ensure the database is clean
        db.drop_all()
        db.create_all()

        timezone = readConf("systemConfig", "timezone")

        # Create a test user
        self.test_user = Users(
            userID=uuidGen(),
            username='testuser',
            password=md5Calc('testpassword'),
            role='user'
        )
        db.session.add(self.test_user)
        db.session.commit()

        # Create a test podcast category
        self.test_category = PodCategory(
            categoryID=uuidGen(),
            categoryName='Test Category'
        )
        db.session.add(self.test_category)
        db.session.commit()

        # Create a test podcast
        self.test_podcast = Podcasts(
            podID=uuidGen(),
            userID=self.test_user.userID,
            categoryID=self.test_category.categoryID,
            podName='Test Podcast',
            podUrl='http://example.com',
            updateDate=getTime(timezone)
        )
        db.session.add(self.test_podcast)
        db.session.commit()

        # Create a test library
        self.test_library = Library(
            libraryID=uuidGen(),
            userID=self.test_user.userID,
            libraryName='Test Library'
        )
        db.session.add(self.test_library)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user(self):
        response = self.client.post('/register', data=dict(username='newuser', password='newpass'))
        self.assertEqual(response.status_code, 201)
        self.assertIn('userID', response.get_json())

    def test_login_user(self):
        response = self.client.post('/login', data=dict(username='testuser', password='testpassword'))
        self.assertEqual(response.status_code, 201)
        json_data = response.get_json()
        self.assertIn('Token', json_data)
        return json_data['Token']

    def test_add_and_get_notes(self):
        token = self.test_login_user()
        response = self.client.post('/addnote', data=dict(tokenID=token, content='Test Note', podid=self.test_podcast.podID))
        self.assertEqual(response.status_code, 200)
        note_id = response.get_json()['noteID']

        response = self.client.post('/listnotes', data=dict(tokenID=token))
        notes = response.get_json()

        self.assertIsNotNone(notes)
        self.assertTrue(isinstance(notes, list))
        self.assertTrue(any(note['NoteID'] == note_id for note in notes))
    
    def test_multiple_note_creation(self):
        token = self.test_login_user()
        for i in range(100):  # Simulate creating 100 notes
            response = self.client.post('/addnote', data=dict(
                tokenID=token,
                content=f'Test Note {i}',
                podid=self.test_podcast.podID
            ))
        self.assertEqual(response.status_code, 200)
        self.assertIn('noteID', response.get_json())

    def test_add_podcast(self):
        token = self.test_login_user()
        response = self.client.post('/addpodcast', data=dict(
        tokenID=token,
        podName='New Podcast',
        podUrl='http://example.com',
        categoryID=self.test_category.categoryID
        ))

        # Check that the podcast was added successfully and a PodcastID is returned
        self.assertEqual(response.status_code, 200)
        self.assertIn('PodcastID', response.get_json())

    def test_add_subscription(self):
        token = self.test_login_user()
        response = self.client.post('/addsubscription', data=dict(
            tokenID=token, 
            libID=self.test_library.libraryID  # 使用 libID 而不是 podID
        ))

        self.assertEqual(response.status_code, 200)
        self.assertIn('Status', response.get_json())


    def test_list_subscriptions(self):
        token = self.test_login_user()
        # Add a subscription to ensure there is data to list
        self.test_add_subscription()
        response = self.client.post('/listsubscription', data=dict(tokenID=token))
        # Check that the response is a list and contains the subscribed library
        self.assertEqual(response.status_code, 200)
        subscriptions = response.get_json()
        self.assertTrue(isinstance(subscriptions, list))
        self.assertTrue(any(sub['LibraryID'] == self.test_library.libraryID for sub in subscriptions))  # Updated key name

    def test_delete_podcast(self):
        token = self.test_login_user()
        response = self.client.post('/deletepodcast', data=dict(
            tokenID=token, 
            podID=self.test_podcast.podID
            ))

        self.assertIn('Status', response.get_json())

    def test_add_snippet(self):
        token = self.test_login_user()  
        response = self.client.post('/addsnippet', data=dict(
            tokenID=token,
            content='This is a test snippet',
            podid=self.test_podcast.podID
        ))
        self.assertIn('SnippetID', response.get_json())

if __name__ == '__main__':
    unittest.main()
# import os
# import unittest
# import uuid
# from app import create_app, db
# from models.sqlmodel import Library, Users, Podcasts, PodCategory, Notes, Subscriptions
# from utils import uuidGen, md5Calc, getTime
# from unittest.mock import patch

# class BasicTests(unittest.TestCase):

#     def setUp(self):
#         """Set up the test client and initialize the database."""
#         self.app = create_app('testing')
#         self.client = self.app.test_client()
#         self.app_context = self.app.app_context()
#         self.app_context.push()

#         # Initialize the database
#         db.create_all()

#         # Create initial test data with unique user
#         self.create_test_user(username=f'testuser_{uuid.uuid4()}')
#         self.create_test_category()
#         self.create_test_podcast()
#         self.create_test_library()

#         # Create a dummy podcast file for testing
#         self.create_dummy_file('test_podcast.mp3', b'Test Podcast Content')

#     def tearDown(self):
#         """Tear down the test environment."""
#         # Clean up files created during testing
#         self.cleanup_test_files(['test_podcast.mp3', 'test_voice_note.mp3'])

#         # Remove the session and drop the database
#         db.session.remove()
#         db.drop_all()

#         # Pop the app context
#         self.app_context.pop()

#     def create_test_user(self, username):
#         """Create a test user with a unique username."""
#         user = user(userID=str(uuid.uuid4()), username=username, password='password', firstname='test', lastname='user', dob='2000-01-01')
#         db.session.add(user)
#         db.session.commit()

#     def create_dummy_file(self, file_name, content):
#         """Helper method to create a dummy file for testing."""
#         with open(file_name, 'wb') as f:
#             f.write(content)

#     def cleanup_test_files(self, files):
#         """Helper method to clean up test files."""
#         for file in files:
#             if os.path.exists(file):
#                 os.remove(file)


#     def create_test_user(self):
#         """Create a test user."""
#         self.test_user = Users(
#             userID=uuidGen(),
#             username='testuser',
#             password=md5Calc('testpassword'),
#             firstname = 'test',
#             lastname =  'user',
#             dob = '1/1/2000'
#         )
#         db.session.add(self.test_user)
#         db.session.commit()

#     def create_test_category(self):
#         """Create a test podcast category."""
#         self.test_category = PodCategory(
#             categoryID=uuidGen(),
#             categoryName='Test Category'
#         )
#         db.session.add(self.test_category)
#         db.session.commit()

#     def create_test_podcast(self):
#         """Create a test podcast."""
#         self.test_podcast = Podcasts(
#             podID=uuidGen(),
#             userID=self.test_user.userID,
#             categoryID=self.test_category.categoryID,
#             podName='Test Podcast',
#             podUrl='http://example.com',
#             updateDate=getTime('UTC')
#         )
#         db.session.add(self.test_podcast)
#         db.session.commit()

#     def create_test_library(self):
#         """Create a test library."""
#         self.test_library = Library(
#             libraryID=uuidGen(),
#             userID=self.test_user.userID,
#             libraryName='Test Library'
#         )
#         db.session.add(self.test_library)
#         db.session.commit()

#     def test_register_user(self):
#         """Test user registration."""
#         response = self.client.post('/register', data=dict(username='newuser', password='newpass'))
#         self.assertEqual(response.status_code, 201)
#         self.assertIn('userID', response.get_json())

#     def test_login_user(self):
#         """Test user login."""
#         response = self.client.post('/login', data=dict(username='testuser', password='testpassword'))
#         self.assertEqual(response.status_code, 201)
#         json_data = response.get_json()
#         self.assertIn('Token', json_data)

#     def login_and_get_token(self):
#         """Helper method to log in and return a token."""
#         response = self.client.post('/login', data=dict(username='testuser', password='testpassword'))
#         json_data = response.get_json()
#         return json_data['Token']


#     def test_access_without_token(self):
#         """Test accessing a route without a token."""
#         response = self.client.post('/listnotes')
#         self.assertEqual(response.status_code, 401)

#     def test_add_podcast(self):
#         """Test adding a podcast."""
#         token = self.login_and_get_token()
#         with self.app.test_client() as client:
#             with open('test_podcast.mp3', 'wb') as f:
#                 f.write(b'Test Podcast Content')
#             with open('test_podcast.mp3', 'rb') as podcast_file:
#                 response = client.post('/addpodcast', data={
#                     'tokenID': token,
#                     'podName': 'New Podcast',
#                     'categoryID': self.test_category.categoryID,
#                     'file': podcast_file
#                 })
#                 self.assertEqual(response.status_code, 200)
#                 self.assertIn('PodcastID', response.get_json())
#                 podcast_id = response.get_json()['PodcastID']
        
#         # Clean up: Delete the generated podcast file from the server
#         # Assuming there's a method or route to delete podcasts by ID
#         response = client.post('/deletepodcast', data={
#             'tokenID': token,
#             'podID': podcast_id
#         })
#         self.assertEqual(response.status_code, 200)

#         # Clean up: Delete the local test file
#         os.remove('test_podcast.mp3')

    

#     def test_delete_podcast(self):
#         """Testing deleteing a podcast."""
        
#         token = self.login_and_get_token()
#         with open('test_podcast.mp3', 'rb') as podcast_file:
#             response = self.client.post('/addpodcast', data={
#             'tokenID': token,
#             'podName': 'Podcast to Delete',
#             'categoryID': self.test_category.categoryID,
#             'file': podcast_file
#         })
#             self.assertEqual(response.status_code, 200)
#             podcast_id = response.get_json()['PodcastID']

    
#         response = self.client.post('/deletepodcast', data=dict(tokenID=token, podID=podcast_id))
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Status', response.get_json())
        

#     def test_add_subscription(self):
#         """Test adding a subscription."""
#         token = self.login_and_get_token()
#         response = self.client.post('/addsubscription', data=dict(tokenID=token, libID=self.test_library.libraryID))
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Status', response.get_json())

#     def test_list_subscriptions(self):
#         """Test listing subscriptions."""
#         token = self.login_and_get_token()
#         self.test_add_subscription()
#         response = self.client.post('/listsubscription', data=dict(tokenID=token))
#         self.assertEqual(response.status_code, 200)
#         subscriptions = response.get_json()
#         self.assertTrue(isinstance(subscriptions, list))
#         self.assertTrue(any(sub['LibraryID'] == self.test_library.libraryID for sub in subscriptions))

#     def test_user_workflow(self):
#         """Test a full user workflow."""
#         token = self.login_and_get_token()
#         response = self.client.post('/addnote', data=dict(tokenID=token, content='Workflow Note', podid=self.test_podcast.podID))
#         self.assertEqual(response.status_code, 200)
#         response = self.client.post('/listnotes', data=dict(tokenID=token))
#         notes = response.get_json()
#         self.assertTrue(any(note.get('NoteID') for note in notes))

#     def test_register_user_with_long_username(self):
#         """Test registration with a long username."""
#         long_username = 'a' * 256
#         response = self.client.post('/register', data=dict(username=long_username, password='testpass'))
#         self.assertEqual(response.status_code, 400)


#     def test_add_and_get_notes(self):
#         """Test adding a note and retrieving it."""
#         token = self.login_and_get_token()
#         response = self.client.post('/addnote', data=dict(tokenID=token, content='Test Note', podid=self.test_podcast.podID))
#         self.assertEqual(response.status_code, 200)
#         note_id = response.get_json()['noteID']

#         response = self.client.post('/listnotes', data=dict(tokenID=token))
#         notes = response.get_json()

#         self.assertIsNotNone(notes)
#         self.assertTrue(isinstance(notes, list))
#         self.assertTrue(any(note.get('NoteID') == note_id for note in notes))
        
#     def test_concurrent_note_creation(self):
#         """Test concurrent note creation."""
#         token = self.login_and_get_token()
#         for i in range(10):
#             response = self.client.post('/addnote', data=dict(tokenID=token, content=f'Test Note {i}', podid=self.test_podcast.podID))
#             self.assertEqual(response.status_code, 200)
#         response = self.client.post('/listnotes', data=dict(tokenID=token))
#         notes = response.get_json()
#         self.assertEqual(len(notes), 10)
    
    
#     def test_delete_note(self):
#         """Test deleting a note."""
#         token = self.login_and_get_token()
#         response = self.client.post('/addnote', data=dict(tokenID=token, content='Note to Delete', podid=self.test_podcast.podID))
#         self.assertEqual(response.status_code, 200)
#         note_id = response.get_json()['noteID']
#         response = self.client.post('/deletenote', data=dict(tokenID=token, noteID=note_id))
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Status', response.get_json())

    
#     def test_upload_voice_note(self):
#         """Test uploading a voice note."""
#         token = self.login_and_get_token()
#         with self.app.test_client() as client:
#             with open('test_voice_note.mp3', 'wb') as f:
#                 f.write(b'Test Voice Note Content')
#             with open('test_voice_note.mp3', 'rb') as voice_note_file:
#                 response = client.post('/uploadvoicenote', data={
#                     'tokenID': token,
#                     'file': voice_note_file
#                 })
#                 self.assertEqual(response.status_code, 200)
#                 self.assertIn('Status', response.get_json())
                
#     def test_register_user_with_empty_username(self):
#         """Test registration with an empty username."""
#         response = self.client.post('/register', data=dict(username='', password='testpass'))
#         self.assertEqual(response.status_code, 400)

#     def test_register_user_with_duplicate_username(self):
#         """Test registration with a duplicate username."""
#         response = self.client.post('/register', data=dict(username='testuser', password='testpass'))
#         self.assertEqual(response.status_code, 409)  # Assuming 409 is the conflict error for duplicate username

#     def test_addnote_without_token(self):
#         """Test adding a note without providing a token."""
#         response = self.client.post('/addnote', data=dict(content='Test Note', podid=self.test_podcast.podID))
#         self.assertEqual(response.status_code, 400)  # Assuming 400 for bad request

#     def test_addnote_without_content(self):
#         """Test adding a note without content."""
#         token = self.login_and_get_token()
#         response = self.client.post('/addnote', data=dict(tokenID=token, podid=self.test_podcast.podID))
#         self.assertEqual(response.status_code, 400)

#     def test_database_error_handling(self):
#         """Test how the app handles a database error."""
#         token = self.login_and_get_token()
#         with patch('models.sqlmodel.db.session.commit', side_effect=Exception("Database Error")):
#             response = self.client.post('/addnote', data=dict(tokenID=token, content='Test Note', podid=self.test_podcast.podID))
#             self.assertEqual(response.status_code, 500)

#     def cleanup_test_files(self):
#         directories_to_cleanup = {
#             'static/notes': '.mp3',
#             'static/podcasts': '.mp3'
#         }

#         for directory, extension in directories_to_cleanup.items():
#             if os.path.exists(directory):
#                 for file in os.listdir(directory):
#                     if file.endswith(extension):
#                         file_path = os.path.join(directory, file)
#                         try:
#                             os.remove(file_path)
#                             print(f"Deleted file: {file_path}")
#                         except OSError as e:
#                             print(f"Error deleting file {file_path}: {e}")


# if __name__ == '__main__':
#     unittest.main()
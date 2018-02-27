import json
import os
import re

from utils.tests import CrystalPrismTestCase


# Test /api/canvashare/drawing endpoint [POST, GET]
class TestDrawing(CrystalPrismTestCase):
    def test_drawing_post_and_get(self):
        # Arrange
        # Create user and login to get token for Authorization header
        self.create_user()
        self.login()
        header = {'Authorization': 'Bearer ' + self.token}

        # Open drawing.txt to get sample image data URL
        test_drawing = os.path.dirname(__file__) + '/../fixtures/drawing.txt'
        with open(test_drawing, 'r') as drawing:
            drawing = drawing.read()
        data = {'drawing': drawing, 'title': 'Test'}

        # Act
        post_response = self.client.post(
            '/api/canvashare/drawing',
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )

        get_response = self.client.get(
            '/api/canvashare/drawing/' + self.username + '/1.png'
            )

        get_user_response = self.client.get(
            '/api/user',
            headers=header
            )
        user_data = json.loads(get_user_response.get_data(as_text=True))

        # Assert
        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(get_response.mimetype, 'image/png')
        self.assertEqual(user_data['drawing_count'], 1)

    def test_drawing_post_error(self):
        # Act
        post_response = self.client.post('/api/canvashare/drawing')
        error = post_response.get_data(as_text=True)

        # Assert
        self.assertEqual(post_response.status_code, 401)
        self.assertEqual(error, 'Unauthorized')


# Test /api/canvashare/drawing-info endpoint [GET, PATCH]
class TestDrawingInfo(CrystalPrismTestCase):
    def test_drawing_info_get(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '1'
        title = 'Welcome'

        # Act
        response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['title'], title)

    def test_drawing_info_get_error(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '100000'

        # Act
        response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        error = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error, 'Not found')

    def test_drawing_info_patch_view(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '1'
        data = {'request': 'view'}

        # Get current number of views from drawing info file
        initial_response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        response_data = json.loads(initial_response.get_data(as_text=True))
        views = response_data['views']

        # Act
        patch_response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            data=json.dumps(data),
            content_type='application/json'
            )

        get_response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        response_data = json.loads(get_response.get_data(as_text=True))

        # Assert
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(response_data['views'], views + 1)

    def test_drawing_info_patch_view_error(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '100000'
        data = {'request': 'view'}

        # Act
        response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            data=json.dumps(data),
            content_type='application/json'
            )
        error = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error, 'Not found')

    def test_drawing_info_patch_like_and_unlike(self):
        # Arrange (for liking drawing)
        artist_name = 'user'
        drawing_id = '1'

        # Create user and login to get token for Authorization header
        self.create_user()
        self.login()
        header = {'Authorization': 'Bearer ' + self.token}

        data = {'request': 'like'}

        # Get current number of views from drawing info file
        initial_response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        initial_data = json.loads(initial_response.get_data(as_text=True))
        likes = initial_data['likes']

        # Act (for liking drawing)
        patch_response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )

        get_response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        get_response_data = json.loads(get_response.get_data(as_text=True))

        get_user_response = self.client.get(
            '/api/user',
            headers=header
            )
        user_data = json.loads(get_user_response.get_data(as_text=True))

        # Assert (for liking drawing)
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(get_response_data['likes'], likes + 1)
        self.assertEqual(bool(
            self.username in get_response_data['liked_users']
            ), True)
        self.assertEqual(
            user_data['liked_drawings'],
            [artist_name + '/' + drawing_id + '.png']
            )

        # Arrange (for unliking drawing)
        data = {'request': 'unlike'}

        # Act (for unliking drawing)
        patch_response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )

        get_response = self.client.get(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id
            )
        get_response_data = json.loads(get_response.get_data(as_text=True))

        get_user_response = self.client.get(
            '/api/user',
            headers=header
            )
        user_data = json.loads(get_user_response.get_data(as_text=True))

        # Assert (for unliking drawing)
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(get_response_data['likes'], likes)
        self.assertEqual(bool(
            self.username in get_response_data['liked_users']
            ), False)
        self.assertEqual(user_data['liked_drawings'], [])

    def test_drawing_info_patch_verify_error(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '1'
        data = {'request': 'like'}

        # Act
        response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            data=json.dumps(data),
            content_type='application/json'
            )
        error = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 401)
        self.assertEqual(error, 'Unauthorized')

    def test_drawing_info_patch_like_error(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '1'

        # Create user and login to get token for Authorization header
        self.create_user()
        self.login()
        header = {'Authorization': 'Bearer ' + self.token}

        data = {'request': 'like'}

        # Act
        first_response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )

        second_response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )
        second_response_data = second_response.get_data(as_text=True)

        # Assert
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(second_response_data, 'User already liked drawing')

    def test_drawing_info_patch_unlike_error(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '1'

        # Create user and login to get token for Authorization header
        self.create_user()
        self.login()
        header = {'Authorization': 'Bearer ' + self.token}

        data = {'request': 'unlike'}

        # Act
        response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )
        response_data = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, 'User did not like drawing')

    def test_drawing_info_patch_not_found_error(self):
        # Arrange
        artist_name = 'user'
        drawing_id = '100000'

        # Create user and login to get token for Authorization header
        self.create_user()
        self.login()
        header = {'Authorization': 'Bearer ' + self.token}

        data = {'request': 'like'}

        # Act
        response = self.client.patch(
            '/api/canvashare/drawing-info/' + artist_name + '/' + drawing_id,
            headers=header,
            data=json.dumps(data),
            content_type='application/json'
            )
        error = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error, 'Not found')


# Test /api/canvashare/gallery endpoint [GET]
class TestGallery(CrystalPrismTestCase):
    def test_gallery_get(self):
        # Act
        response = self.client.get('/api/canvashare/gallery')
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data), 10)

        # Ensure response is a list of drawing file paths
        pattern = re.compile(r'^[a-zA-Z0-9-_]*[/]\d{1,}\.png$')
        filtered_response = filter(pattern.match, response_data)
        self.assertEqual(len([i for i in filtered_response]), 10)

    def test_gallery_get_none(self):
        # Arrange
        data = {'start': 100}

        # Act
        response = self.client.get(
            '/api/canvashare/gallery',
            query_string=data
            )
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(response_data, [])

    def test_gallery_get_partial(self):
        # Arrange
        data = {'end': 5}

        # Act
        response = self.client.get(
            '/api/canvashare/gallery',
            query_string=data
            )
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(len(response_data), 5)

    def test_gallery_get_error(self):
        # Arrange
        data = {'start': 5, 'end': 0}

        # Act
        response = self.client.get(
            '/api/canvashare/gallery',
            query_string=data
            )
        error = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(error, 'Start param cannot be greater than end')

    def test_user_gallery_get(self):
        # Arrange
        artist_name = 'user'

        # Act
        response = self.client.get('/api/canvashare/gallery/' + artist_name)
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data), 10)

        # Ensure response is a list of drawing file paths from artist's folder
        pattern = re.compile(r'^' + artist_name + r'[/]\d{1,}\.png$')
        filtered_response = filter(pattern.match, response_data)
        self.assertEqual(len([i for i in filtered_response]), 10)

    def test_user_gallery_get_none(self):
        # Arrange
        artist_name = 'user'
        data = {'start': 100}

        # Act
        response = self.client.get(
            '/api/canvashare/gallery/' + artist_name,
            query_string=data
            )
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(response_data, [])

    def test_user_gallery_get_partial(self):
        # Arrange
        artist_name = 'user'
        data = {'end': 5}

        # Act
        response = self.client.get(
            '/api/canvashare/gallery/' + artist_name,
            query_string=data
            )
        response_data = json.loads(response.get_data(as_text=True))

        # Assert
        self.assertEqual(len(response_data), 5)

    def test_user_gallery_get_error(self):
        # Arrange
        artist_name = 'user'
        data = {'start': 5, 'end': 0}

        # Act
        response = self.client.get(
            '/api/canvashare/gallery/' + artist_name,
            query_string=data
            )
        error = response.get_data(as_text=True)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(error, 'Start param cannot be greater than end')

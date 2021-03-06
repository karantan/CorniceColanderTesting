"""Tests for views."""

from pyramid import testing

import unittest
import webtest


class TestViews(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('cornice')

        self.config.scan('myapp.views')
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    def tearDown(self):
        testing.tearDown()

    def test_collection_traverse(self):
        resp = self.app.get('/fruits/').json
        self.assertEqual(sorted(resp['fruits']), ['1', '2'])

    def test_get(self):
        resp = self.app.get('/fruits/1/')
        self.assertEqual(
            resp.json,
            {'name': 'apple', 'description': 'sweet, edible fruit'},
        )

        resp = self.app.get('/fruits/2/')
        self.assertEqual(
            resp.json,
            {'name': 'orange', 'description': 'member of the citrus family'},
        )

        self.app.get('/fruits/3/', status=404)

    def test_post_no_info(self):
        resp = self.app.post('/fruits/', {'name': 'banana'})
        self.assertEqual(resp.json, {'name': 'banana', 'info': None})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(
            resp.headers['Location'], 'http://localhost/fruits/3/')

    def test_post_with_info(self):
        resp = self.app.post_json(
            '/fruits/', {'name': 'banana', 'info': {
                'title': 'foo', 'body': 'Test Stuff'},
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(
            resp.headers['Location'], 'http://localhost/fruits/4/')

    def test_post_400(self):
        resp = self.app.post('/fruits/', {'name': 'mango'}, status=400)
        resp = self.app.post_json(
            '/fruits/',
            {'name': 'mango', 'info': {'body': '/'}},
            status=400,
        )

        self.assertEqual(
            resp.json,
            {
                'status': 'error',
                'errors': [{
                    'description': 'Wrong fruit.',
                    'location': 'body',
                    'name': 'mango',
                }, {
                    'description': 'Invalid description.',
                    'location': 'body',
                    'name': '/',
                }],
            },
        )

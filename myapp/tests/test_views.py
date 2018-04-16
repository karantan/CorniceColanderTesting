"""Tests for views."""

from pyramid import testing

import unittest
import webtest


class TestResourceTraverse(unittest.TestCase):

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

    def test_traverse(self):
        resp = self.app.get('/fruits/1/')
        self.assertEqual(resp.json, {'name': 'apple'})

        resp = self.app.get('/fruits/2/')
        self.assertEqual(resp.json, {'name': 'orange'})

        self.app.get('/fruits/3/', status=404)

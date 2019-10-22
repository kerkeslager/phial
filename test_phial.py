import unittest
from unittest import mock

import phial

class ResponseTests(unittest.TestCase):
    def test_content_can_be_positional_argument(self):
        response = phial.Response('Hello, world\n', content_type='text/plain')

        self.assertEqual(response.content, 'Hello, world\n')

    def test_content_can_be_keyword_argument(self):
        response = phial.Response(content='Hello, world\n', content_type='text/plain')

        self.assertEqual(response.content, 'Hello, world\n')

    def test_status_defaults_to_200(self):
        response = phial.Response(
            content_type='text/plain',
            content='Hello, world\n',
        )

        self.assertEqual(response.status, 200)

    def test_headers(self):
        response = phial.Response(
            content_type='text/plain',
            content='Hello, world\n',
        )

        self.assertEqual(
            response.headers,
            (
                ('Content-Type', 'text/plain'),
            ),
        )

class HTMLResponseTests(unittest.TestCase):
    def test_sets_content_type(self):
        response = phial.HTMLResponse('<html><body>Hello, world</body></html>')
        self.assertEqual(response.content_type, 'text/html')

class JSONResponseTests(unittest.TestCase):
    def test_sets_content_type(self):
        response = phial.JSONResponse({ 'foo': 'bar', 'baz': 42 })
        self.assertEqual(response.content_type, 'application/json')

    def test_sets_content(self):
        response = phial.JSONResponse({ 'foo': 'bar', 'baz': 42 })
        self.assertEqual(response.content, '{"foo": "bar", "baz": 42}')

    def test_sets_content_json(self):
        response = phial.JSONResponse({ 'foo': 'bar', 'baz': 42 })
        self.assertEqual(response.content_json, {"foo": "bar", "baz": 42})

class TextResponseTests(unittest.TestCase):
    def test_sets_content_type(self):
        response = phial.TextResponse('Hello, world\n')
        self.assertEqual(response.content_type, 'text/plain')

class _get_status_Tests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(phial._get_status(mock.MagicMock(status=200)), '200 OK')

class _get_content_Tests(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(
            phial._get_content(mock.MagicMock(content=b'Hello, world\n')),
            (b'Hello, world\n',),
        )

    def test_str(self):
        self.assertEqual(
            phial._get_content(mock.MagicMock(content='Hello, world\n')),
            (b'Hello, world\n',),
        )

if __name__ == '__main__':
    unittest.main()

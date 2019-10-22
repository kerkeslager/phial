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

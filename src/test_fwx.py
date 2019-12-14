import unittest
from unittest import mock

import fwx

class RequestTests(unittest.TestCase):
    def test_GET(self):
        request = fwx.Request('GET', '/', {
            'QUERY_STRING': 'foo=bar&baz=qux',
        })

        self.assertEqual(request.GET['foo'], ['bar'])
        self.assertEqual(request.GET['baz'], ['qux'])

    def test_parameters(self):
        request = fwx.Request('GET', '/', {
            'QUERY_STRING': 'foo=bar&baz=qux',
        })

        self.assertEqual(request.parameters['foo'], ['bar'])
        self.assertEqual(request.parameters['baz'], ['qux'])

class ResponseTests(unittest.TestCase):
    def test_content_can_be_positional_argument(self):
        response = fwx.Response('Hello, world\n', content_type='text/plain')

        self.assertEqual(response.content, 'Hello, world\n')

    def test_content_can_be_keyword_argument(self):
        response = fwx.Response(content='Hello, world\n', content_type='text/plain')

        self.assertEqual(response.content, 'Hello, world\n')

    def test_status_defaults_to_200(self):
        response = fwx.Response(
            content_type='text/plain',
            content='Hello, world\n',
        )

        self.assertEqual(response.status, 200)

    def test_headers(self):
        response = fwx.Response(
            content_type='text/plain',
            content='Hello, world\n',
        )

        self.assertEqual(
            response.headers,
            (
                ('Content-Type', 'text/plain'),
                ('X-Content-Type-Options', 'nosniff'),
            ),
        )

class HTMLResponseTests(unittest.TestCase):
    def test_sets_content_type(self):
        response = fwx.HTMLResponse('<html><body>Hello, world</body></html>')
        self.assertEqual(response.content_type, 'text/html')

class JSONResponseTests(unittest.TestCase):
    def test_sets_content_type(self):
        response = fwx.JSONResponse({ 'foo': 'bar', 'baz': 42 })
        self.assertEqual(response.content_type, 'application/json')

    def test_sets_content(self):
        response = fwx.JSONResponse({ 'foo': 'bar', 'baz': 42 })
        self.assertEqual(response.content, '{"foo": "bar", "baz": 42}')

    def test_sets_content_json(self):
        response = fwx.JSONResponse({ 'foo': 'bar', 'baz': 42 })
        self.assertEqual(response.content_json, {"foo": "bar", "baz": 42})

class TextResponseTests(unittest.TestCase):
    def test_sets_content_type(self):
        response = fwx.TextResponse('Hello, world\n')
        self.assertEqual(response.content_type, 'text/plain')

class RedirectResponse(unittest.TestCase):
    def test_takes_location_as_positional_argument(self):
        response = fwx.RedirectResponse('/location')
        self.assertEqual(response.location, '/location')

    def test_takes_location_as_keyword_argument(self):
        response = fwx.RedirectResponse(location='/location')
        self.assertEqual(response.location, '/location')

    def test_permanent_defaults_to_true(self):
        response = fwx.RedirectResponse('/location')
        self.assertEqual(response.permanent, True)

    def test_status(self):
        self.assertEqual(
            fwx.RedirectResponse('/location', permanent=True).status,
            308,
        )
        self.assertEqual(
            fwx.RedirectResponse('/location', permanent=False).status,
            307,
        )

    def test_headers(self):
        self.assertEqual(
            fwx.RedirectResponse('/location').headers,
            (('Location','/location'),),
        )

    def test_content(self):
        self.assertEqual(
            fwx.RedirectResponse('/location').content,
            (b'',),
        )

class _get_status_Tests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(fwx._get_status(mock.MagicMock(status=200)), '200 OK')
        self.assertEqual(fwx._get_status(mock.MagicMock(status=307)), '307 Temporary Redirect')
        self.assertEqual(fwx._get_status(mock.MagicMock(status=308)), '308 Permanent Redirect')

class _get_content_Tests(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(
            fwx._get_content(mock.MagicMock(content=b'Hello, world\n')),
            (b'Hello, world\n',),
        )

    def test_str(self):
        self.assertEqual(
            fwx._get_content(mock.MagicMock(content='Hello, world\n')),
            (b'Hello, world\n',),
        )

class route_on_subpath_Tests(unittest.TestCase):
    def test_routes(self):
        router = fwx.route_on_subpath(
            routes={
                'foo': lambda request: fwx.TextResponse('foo'),
                'bar': lambda request: fwx.TextResponse('bar'),
                'baz': lambda request: fwx.TextResponse('baz'),
            },
        )

        self.assertEqual(
            router(fwx.Request('GET', '/bar/bara/anne/')).content,
            'bar',
        )

    def test_resets_subpath(self):
        router = fwx.route_on_subpath(
            routes={
                'foo': lambda request: fwx.TextResponse('foo'),
                'bar': lambda request: fwx.TextResponse(request.subpath),
                'baz': lambda request: fwx.TextResponse('baz'),
            },
        )

        self.assertEqual(
            router(fwx.Request('GET', '/bar/bara/anne/')).content,
            'bara/anne/',
        )

    def test_leaves_path_intact(self):
        router = fwx.route_on_subpath(
            routes={
                'foo': lambda request: fwx.TextResponse('foo'),
                'bar': lambda request: fwx.TextResponse(request.path),
                'baz': lambda request: fwx.TextResponse('baz'),
            },
        )

        self.assertEqual(
            router(fwx.Request('GET', '/bar/bara/anne/')).content,
            '/bar/bara/anne/',
        )

class default_file_not_found_Tests(unittest.TestCase):
    def test_responds(self):
        response = fwx.default_file_not_found_handler(
            fwx.Request('GET', '/bar/bara/anne/'),
        )

        self.assertNotEqual(response, None)

if __name__ == '__main__':
    unittest.main()

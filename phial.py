import collections
import json

Request = collections.namedtuple(
    'Request',
    (
        'environ',
    )
)

_Response = collections.namedtuple(
    'Response',
    (
        'status',
        'content_type',
        'extra_headers',
        'content',
    ),
)

class Response(_Response):
    def __new__(cls, content, **kwargs):
        status = kwargs.pop('status', 200)
        assert isinstance(status, int)

        content_type = kwargs.pop('content_type')
        assert isinstance(content_type, str)

        extra_headers = kwargs.pop('extra_headers', ())
        assert isinstance(extra_headers, tuple)

        assert len(kwargs) == 0

        return super().__new__(
            cls,
            status=status,
            content_type=content_type,
            extra_headers=extra_headers,
            content=content,
        )

    @property
    def headers(self):
        return (
            ('Content-Type', self.content_type),
        )

class HTMLResponse(Response):
    def __new__(cls, content, **kwargs):
        assert 'content_type' not in kwargs

        return super().__new__(
            cls,
            content,
            content_type='text/html',
            **kwargs,
        )

class JSONResponse(Response):
    def __new__(cls, content_json, **kwargs):
        assert 'content_type' not in kwargs
        assert 'content' not in kwargs

        self = super().__new__(
            cls,
            content=json.dumps(content_json),
            content_type='application/json',
            **kwargs,
        )
        self.content_json = content_json
        return self

class TextResponse(Response):
    def __new__(cls, content, **kwargs):
        assert 'content_type' not in kwargs

        return super().__new__(
            cls,
            content,
            content_type='text/plain',
            **kwargs,
        )

_RedirectResponse = collections.namedtuple(
    'RedirectResponse',
    (
        'location',
        'permanent',
    ),
)

class RedirectResponse(_RedirectResponse):
    def __new__(cls, location, **kwargs):
        assert isinstance(location, str)

        permanent = kwargs.pop('permanent', True)
        assert isinstance(permanent, bool)
        assert len(kwargs) == 0

        return super().__new__(
            cls,
            location=location,
            permanent=permanent,
        )

    @property
    def status(self):
        return 308 if self.permanent else 307

    @property
    def headers(self):
        return (('Location', self.location),)

    @property
    def content(self):
        return (b'',)

def _get_status(response):
    return {
        200: '200 OK',
        307: '307 Temporary Redirect',
        308: '308 Permanent Redirect',
    }[response.status]

def _get_headers(response):
    return list(response.headers)

def _get_content(response):
    content = response.content

    if isinstance(content, bytes):
        return (content,)

    if isinstance(content, str):
        return (content.encode('utf-8'),)

    return content

def App(handler):
    def app(environ, start_fn):
        response = handler(Request(environ))

        start_fn(_get_status(response), _get_headers(response))
        return _get_content(response)
    return app

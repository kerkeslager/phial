import collections

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

class TextResponse(Response):
    def __new__(cls, content, **kwargs):
        assert 'content_type' not in kwargs
        return super().__new__(
            cls,
            content,
            content_type='text/plain',
            **kwargs,
        )

def _get_status(response):
    return {
        200: '200 OK',
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

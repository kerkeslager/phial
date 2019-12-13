import collections
import http.cookies
import json
import urllib.parse

_Request = collections.namedtuple(
    'Request',
    (
        'env',
        'GET',
        'accept',
        'accept_encoding',
        'accept_language',
        'content',
        'content_length',
        'content_type',
        'cookie',
        'method',
        'path',
        'parameters',
        'query',
        'user_agent',
    )
)

class Request(_Request):
    def __new__(cls, env):
        errors = []

        accept = env.get('HTTP_ACCEPT')
        accept_encoding = env.get('HTTP_ACCEPT_ENCODING')
        accept_language = env.get('HTTP_ACCEPT_LANGUAGE')
        content = env.get('CONTENT', '')
        content_type = env.get('CONTENT_TYPE')
        method = env.get('REQUEST_METHOD')
        path = env.get('PATH_INFO')
        query = env.get('QUERY_STRING')
        user_agent = env.get('HTTP_USER_AGENT')

        content_length = env.get('CONTENT_LENGTH')

        if content_length == '' or content_length is None:
            content_length = 0
        else:
            try:
                content_length = int(content_length)
            except ValueError:
                errors.append('Unable to parse Content-Length "{}"'.format(content_length))
                content_length = 0

        try:
            cookie = http.cookies.SimpleCookie(env.get('HTTP_COOKIE'))
        except:
            cookie = http.cookies.SimpleCookie()


        try:
            GET = urllib.parse.parse_qs(query)
        except:
            GET = {}
            errors.append('Unable to parse GET parameters from query string "{}"'.format(query))

        if method == 'GET':
            parameters = GET

        result = super().__new__(
            cls,
            env=env,
            GET=GET,
            accept=accept,
            accept_encoding=accept_encoding,
            accept_language=accept_language,
            content = content,
            content_length = content_length,
            content_type = content_type,
            cookie=cookie,
            method=method,
            parameters=parameters,
            path=path,
            query=query,
            user_agent=user_agent,
        )

        result.subpath = path
        return result

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

REQUEST_METHODS = (
    'GET',
    'HEAD',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'CONNECT',
    'OPTIONS',
    'TRACE',
)

def default_method_not_allowed_handler(request):
    return Response('')

def default_options_handler(handlers):
    def handler(request):
        return Response(','.join(handlers.keys()))
    return handler

def route_on_method(**kwargs):
    handlers = {}
    for method in REQUEST_METHODS:
        if method in kwargs:
            handlers[method] = kwargs.pop(method)

    method_not_allowed_handler = kwargs.pop(
        'method_not_allowed',
        default_method_not_allowed_handler,
    )

    assert len(kwargs) == 0

    if 'OPTIONS' not in handlers:
        handlers['OPTIONS'] = default_options_handler(handlers)

    def handler(request):
        return handlers.get(
            request.method.upper(),
            method_not_allowed_handler,
        )(request)

    return handler

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
    def app(env, start_fn):
        response = handler(Request(env))

        start_fn(_get_status(response), _get_headers(response))
        return _get_content(response)
    return app
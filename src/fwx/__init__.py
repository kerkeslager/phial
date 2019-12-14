import collections
import http.cookies
import json
import urllib.parse

_Request = collections.namedtuple(
    'Request',
    (
        'env',
        'GET',
        'POST',
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
    def __new__(cls, method, path, env=None):
        if env is None:
            env = {}

        errors = []

        accept = env.get('HTTP_ACCEPT')
        accept_encoding = env.get('HTTP_ACCEPT_ENCODING')
        accept_language = env.get('HTTP_ACCEPT_LANGUAGE')
        content = env.get('CONTENT', '')
        content_type = env.get('CONTENT_TYPE')
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

        if method == 'POST':
            try:
                if content_type == 'application/x-www-form-urlencoded':
                    POST = urllib.parse.parse_qs(content)
                else:
                    POST = {}
                    errors.append('Unable to parse POST parameters from content string "{}"'.format(content))

            except:
                POST = {}
                errors.append('Unable to parse POST parameters from content string "{}"'.format(content))

        else:
            POST = {}

        if method == 'GET':
            parameters = GET
        elif method == 'POST':
            parameters = POST
        else:
            parameters = None

        result = super().__new__(
            cls,
            env=env,
            GET=GET,
            POST=POST,
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

        if path.startswith('/'):
            result.subpath = path[1:]
        else:
            result.subpath = path

        return result

def _get_request_from_env(env):
    method = env.get('REQUEST_METHOD')
    path = env.get('PATH_INFO')
    return Request(method, path, env)

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

        extra_headers = kwargs.pop('extra_headers', {})
        assert isinstance(extra_headers, dict)

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
        # Start with the defaults
        result = {
            'X-Content-Type-Options': 'nosniff',
        }

        result = {**result, **(self.extra_headers)}

        builtin_headers = {
            'Content-Type': self.content_type,
        }

        for key, value in builtin_headers.items():
            if key in result:
                raise Exception('Header "{}" defined twice'.format(key))
            else:
                result[key] = value

        return tuple(sorted(result.items()))


class HTMLResponse(Response):
    def __new__(cls, content, **kwargs):
        assert 'content_type' not in kwargs

        return super().__new__(
            cls,
            content,
            content_type='text/html; charset=utf-8',
            **kwargs,
        )

class JSONResponse(Response):
    def __new__(cls, content_json, **kwargs):
        assert 'content_type' not in kwargs
        assert 'content' not in kwargs

        self = super().__new__(
            cls,
            content=json.dumps(content_json),
            content_type='application/json; charset=utf-8',
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
            content_type='text/plain; charset=utf-8',
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

def default_file_not_found_handler(request):
    return TextResponse(
        'Path "{}" with query "{}" not found'.format(request.path, request.query),
        status=404,
    )

def route_on_subpath(**kwargs):
    routes = kwargs.pop('routes')
    file_not_found_handler = kwargs.pop(
        'file_not_found_handler',
        default_file_not_found_handler,
    )

    if routes is None:
        raise Exception('Keyword argument "routes" is required')

    if len(kwargs) > 0:
        raise Exception('Unexpected keyword argument')

    def wrapped(request):
        split_subpath = request.subpath.split('/', 1)
        subpath = split_subpath[0]

        if len(split_subpath) == 2:
            request.subpath = split_subpath[1]
        else:
            request.subpath = ''

        return routes.get(subpath, file_not_found_handler)(request)

    return wrapped

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
    return TextResponse('', status=405)

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
        100: '100 Continue',
        101: '101 Switching Protocols',
        200: '200 OK',
        201: '201 Created',
        202: '202 Accepted',
        203: '203 Non-Authoritative Information',
        204: '204 No Content',
        205: '205 Reset Content',
        300: '300 Multiple Choices',
        301: '301 Moved Permanently',
        304: '304 Not Modified',
        307: '307 Temporary Redirect',
        308: '308 Permanent Redirect',
        400: '400 Bad Request',
        401: '401 Unauthorized',
        402: '402 Payment Required',
        403: '403 Forbidden',
        404: '404 Not Found',
        405: '405 Method Not Allowed',
        406: '406 Not Acceptable',
        409: '409 Conflict',
        410: '410 Gone',
        411: '411 Length Required',
        412: '412 Precondition Failed',
        413: '413 Payload Too Large',
        414: '414 URI Too Long',
        415: '415 Unsupported Media Type',
        416: '416 Range Not Satisfiable',
        417: '417 Expectation Failed',
        418: "418 I'm a teapot",
        429: '429 Too Many Requests',
        431: '431 Request Header Fields Too Large',
        451: '451 Unavailable For Legal Reasons',
        500: '500 Internal Server Error',
        501: '501 Not Implemented',
        503: '503 Service Unavailable',
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
        response = handler(_get_request_from_env(env))

        start_fn(_get_status(response), _get_headers(response))
        return _get_content(response)
    return app

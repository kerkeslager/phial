import collections

Request = collections.namedtuple(
    'Request',
    (
        'environ',
    )
)

Response = collections.namedtuple(
    'Response',
    (
        'status',
        'headers',
        'content',
    ),
)

def App(handler):
    def app(environ, start_fn):
        response = handler(Request(environ))

        start_fn(response.status, response.headers)
        return response.content
    return app

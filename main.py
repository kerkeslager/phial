import fwx

def handler(request):
    return fwx.TextResponse(
        content='Hello, world\n',
    )

app = fwx.App(handler)

if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.web.server import Site
    from twisted.web.wsgi import WSGIResource

    reactor_args = {}
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(5000, site)
    reactor.run(**reactor_args)

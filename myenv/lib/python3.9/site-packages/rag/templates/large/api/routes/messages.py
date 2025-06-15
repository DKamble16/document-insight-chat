def ping(request):
    return {'data': 'pong!'}


def echo(request):
    return request.data

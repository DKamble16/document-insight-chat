import os
from rag import Application
from rag import models, abort, validate, v
from django.views.decorators.csrf import csrf_exempt


# settings
environment = os.environ.get('RAG_ENV', 'development')
settings = {
    'DEBUG': environment == 'development',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': f'{environment}.sqlite3',
        }
    }
}
settings['SECRET_KEY'] = os.environ['DJANGO_SECRET'] if environment == 'production' else ''


# application
app = Application(__name__, settings)


# models
class Message(models.Model):
    text = models.TextField()


# routes
# create a message
@app.route('messages', 'POST', [csrf_exempt])
@validate({
    'text': v.am.string
})
def create_message(request):
    return Message.create(request.data)

# get a message
@app.route('messages/<int:id>', 'GET')
def get_message(request, id):
    return Message.objects.filter(id=id).first() or abort(404)

# get all messages
@app.route('messages', 'GET')
def index_messages(request):
    return Message.objects.all()

# update a message
@app.route('messages/<int:id>', 'PUT', [csrf_exempt])
@validate({
    'text': v.am.string
})
def update_message(request, id):
    message = Message.objects.filter(id=id).first() or abort(404)
    return message.update(request.data).save()

# delete a message
@app.route('messages/<int:id>', 'DELETE', [csrf_exempt])
def destroy_message(request, id):
    message = Message.objects.filter(id=id).first() or abort(404)
    message.delete()
    return message

from rag import abort, validate, v
from .models import Message, User


# create a message
@validate({
    'text': v.am.string,
    'user': v.to.model(User),
})
def create_message(request):
    return Message.create(request.data)

# get a message
def get_message(request, id):
    return Message.objects.filter(id=id).first() or abort(404)

# get all messages
def index_messages(request):
    return Message.objects.all()

# update a message
@validate({
    'text': v.am.string
})
def update_message(request, id):
    message = Message.objects.filter(id=id).first() or abort(404)
    return message.update(request.data).save()

# delete a message
def destroy_message(request, id):
    message = Message.objects.filter(id=id).first() or abort(404)
    message.delete()
    return message

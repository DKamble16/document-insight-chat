from rag import models


class Message(models.Model):
    sender = models.CharField(max_length=200)
    text = models.TextField()

from django.db import models

class Conversation(models.Model):
    user_question = models.TextField()
    bot_answer = models.TextField()
    image_name = models.CharField(max_length=255, blank=True, null=True)  # Store image name

    def __str__(self):
        return f":User  {self.user_question}, Bot: {self.bot_answer}"
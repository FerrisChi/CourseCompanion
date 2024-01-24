from django.db import models
# from django.contrib.auth import get_user_model
import secrets
from django.conf import settings

# User = get_user_model()

# Create your models here.


# class Answer(models.Model):
#     writer = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=100)
#     description = models.TextField()
#     main_keyword = models.CharField(max_length=100)
#     recommand_keyword = models.CharField(max_length=100)
#     category = models.CharField(max_length=100)
#     type = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


student_schema = {
    "properties": {
        "degree": {"type": "string"},
        "department": {"type": "string"},
        "interest": {"type": "string"},
        "goal": {"type": "string"},
        "experience": {"type": "string"},
        "course_taken": {"type": "string"},
        "extra_info": {"type": "string"},
    },
    "required": ["degree", "department", "interest", "goal", "experience", "course_taken"],
}

course_schema = {
    "properties": {
        "code": {"type": "string"},
        "name": {"type": "string"},
        "score": {"type": "integer"},
        "reason": {"type": "string"},
    },
    "required": ["code", "name", "score", "reason"],
}


def generate_secure_random_id():
    min_value = 10 ** 10  # Minimum value of the range (inclusive)
    max_value = 10 ** 11 - 1  # Maximum value of the range (exclusive)
    return secrets.randbelow(max_value - min_value) + min_value


class Conversation(models.Model):
    """
    Conversation model representing a chat conversation.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('ended', 'Ended'),
    ]

    id = models.BigIntegerField(primary_key=True, default=generate_secure_random_id, editable=False)
    title = models.CharField(max_length=255, default="Conversation")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourite = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Conversation #{self.id}: {self.title} - {self.user.username}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    is_from_user = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message {self.id} - {self.content}"
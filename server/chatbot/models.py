from django.db import models
from django.contrib.auth import get_user_model

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

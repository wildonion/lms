


from email.policy import default
from django.db import models
from django.utils import timezone


class FunQuiz(models.Model):
    qna = models.JSONField(default=[])
    time = models.CharField(max_length=25, default='')
    result_stmt = models.JSONField(default={})
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(auto_now=True)

    
class UserFunQuiz(models.Model):
    user_email = models.CharField(max_length=100, default='')
    result = models.IntegerField(default=-1)





from django.db import models
from django.utils import timezone


class Quizz(models.Model):
    teacher_id = models.IntegerField(default=0) # NOTE - the superuser or teacher id 
    course_id = models.IntegerField(default=0)
    course_slug = models.CharField(max_length=250)
    title = models.CharField(max_length=250, unique=True)
    content = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now())
    expiration_time = models.CharField(max_length=25, default='')
    updated_at = models.DateTimeField(auto_now=True)
    
    
class UserQuizz(models.Model):
    user_id = models.IntegerField(default=0)
    quiz_id = models.IntegerField(default=0)
    current_index_question = models.IntegerField(default=0)
    shuffled_content = models.JSONField()
    start_time = models.CharField(max_length=100, default='')
    remaining_time = models.CharField(max_length=100, default='')
    finish_time = models.CharField(max_length=100, default='')
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from courses.models import Course



class Product(models.Model):
    # NOTE - a course might have built either for videos or quiz  
    # NOTE - if they buy a quiz means they bought the course which only has the quiz
    # NOTE - if they buy a course means they bought the course which only has the its videos and might be a quiz for the final exam
    # NOTE - they can buy a course which has a quiz tho, cause the course_id will be saved inside the Quizz table
    course_id = models.IntegerField(default=0)
    mean_score = models.IntegerField(default=0, validators=[MaxValueValidator(50), MinValueValidator(0)]) # NOTE - client must divide the mean_score by 10 to show something in range 0 to 5 
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now())
    last_updated_at = models.DateTimeField(auto_now=True)
    mean_score_counter = models.BigIntegerField(default=0)

    # def save(self, *args, **kwargs):
    #     self.created_at = timezone.now()
    #     self.last_updated_at = timezone.now()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return str(self.course)



class Discount(models.Model):
    code = models.CharField(max_length=150, blank=True, null=True)
    offpercentage = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
    product_id = models.IntegerField(default=0)
    status = models.CharField(max_length=10, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    is_expired = models.IntegerField(default=0) # NOTE - 0 means not expired and 1 means is expired
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.short_description
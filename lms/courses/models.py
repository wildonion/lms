from enum import unique
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from courses.image_validation import image_size_validator
from courses.upload_path import upload_image_path, upload_video_path, upload_video_image_path
from courses.video_validation import video_size_validator, video_content_type_validator
from portal.models import PaymentInfo



class Course(models.Model):
    class PublishedObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status='published')

    status_options = (('draft', 'Draft'), ('published', 'Published'),)
    level_options = (('Conceptual', 'conceptual'), ('Practical', 'practical'), ('Deep', 'deep'),)

    title = models.CharField(max_length=250, unique=True)
    short_description = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    slug = models.SlugField(null=False, db_index=True)
    publish_time = models.DateTimeField(default=None, null=True)
    last_publish_time = models.DateTimeField(default=None, null=True)
    teacher_id = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=status_options, default='draft')
    level = models.CharField(max_length=50, choices=level_options)
    video_count = models.IntegerField(default=0)
    visit_count = models.IntegerField(default=0)
    tags = models.JSONField(default=[])
    image = models.ImageField(upload_to=upload_image_path, max_length=100, null=True, validators=[image_size_validator])
    objects = models.Manager()  # default manager
    published_objects = PublishedObjects()  # custom manager

    class Meta:
        ordering = ('-publish_time',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)  # product no 1 ==> product-no-1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # def get_api_url(self):
    #     return reverse('course-api:listcreate', kwargs={'slug': self.slug})



class Video(models.Model):
    video_name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(null=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now())
    # clip = models.FileField(upload_to=upload_video_path, null=True, validators=[video_size_validator, video_content_type_validator])
    course_id = models.IntegerField(default=0)
    image = models.ImageField(upload_to=upload_video_image_path, max_length=100, null=True, validators=[image_size_validator])
    part = models.IntegerField(blank=True, null=True)
    short_description = models.TextField()
    video_playlist_url = models.URLField(null=False, default='')
    video_duration = models.IntegerField(default=0, null=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.video_name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.video_name
    
    
class User_Video(models.Model):
    video_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    course_id = models.IntegerField(default=0)
    current_process_percentage = models.FloatField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])



class Prerequisite(models.Model):
    main_course = models.IntegerField(default=0)
    prerequisite_courses = models.ManyToManyField(Course, related_name='course_prerequisite', null=True, blank=True)





class User_Course(models.Model):
    payment_info_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    course_id = models.IntegerField(default=0)
    bought_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(auto_now=True)
    passed_percentage = models.FloatField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)]) # NOTE - total current_process_percentage of all course videos / number of videos
    quiz_score = models.IntegerField(default=0)
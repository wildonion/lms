from email.policy import default
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from posts.upload_path import upload_image_path
from posts.image_validation import image_size_validator
from posts.image_validation import image_size_validator
from posts.video_validation import video_size_validator, video_content_type_validator
from posts.upload_path import upload_image_path, ckeditor_upload_video_path, ckeditor_upload_image_path
from cats.models import Cat



class Post(models.Model):
    class PublishedObjects(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status='published')

    title = models.CharField(max_length=250, unique=True)
    short_description = models.TextField(null=True)
    content = models.TextField()
    slug = models.SlugField(null=False, db_index=True)
    publish_time = models.DateTimeField(default=None, null=True)
    last_publish_time = models.DateTimeField(default=None, null=True)
    user_id = models.IntegerField(default=0)
    visit_count = models.IntegerField(default=0)
    tags = models.JSONField(default=[])
    categ = models.ManyToManyField(Cat, related_name='post_cats', null=True, blank=True)
    image = models.ImageField(upload_to=upload_image_path, max_length=100, null=True, validators=[image_size_validator])
    options = (('draft', "Draft"), ('published', 'Published'))
    status = models.CharField(max_length=10, choices=options, default='draft')
    objects = models.Manager()  # default manager
    published_objects = PublishedObjects()  # custom manager

    class Meta:
        ordering = ('-publish_time',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # def get_api_url(self):
    #     return reverse('post-api:detail', kwargs={'slug': self.slug})




class CkeditorImage(models.Model):
    image = models.ImageField(upload_to=ckeditor_upload_image_path, max_length=100, null=True, validators=[image_size_validator])
    
    
class CkeditorVideo(models.Model):
    video = models.FileField(upload_to=ckeditor_upload_video_path, null=True, validators=[video_size_validator, video_content_type_validator])
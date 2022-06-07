


import os
from django.db import models
from rest_framework import validators
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .utils import ContentTypeRestrictedFileField



def upload_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"images/avatars/users/{instance.user_id}/{now:%Y-%m-%d-%H-%M-%S}{milliseconds}{extension}"


class OTPModel(models.Model):
    user_id = models.IntegerField(default=0)
    receptor = models.CharField(max_length=20, unique=True)
    recent_code = models.CharField(max_length=10, default='') # NOTE - will be updated on every request to the service provider with a new generated code
    login_counter = models.BigIntegerField(default=0) # NOTE - will be updated on successful login once the otp code is a valid and not a expired one
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    otp_type = models.SmallIntegerField(default=0) # NOTE - 0 means otp type is signup and 1 means forgot password
    
    
class GoogleMetaData(models.Model):
    user_id = models.IntegerField()
    email = models.CharField(max_length=200, default='')
    google_id = models.CharField(max_length=500, default='')
    image_url = models.CharField(max_length=500, default='')
    
    


class OTPMetaData(models.Model):
    otp_id = models.IntegerField()
    receptor = models.CharField(max_length=20, default='')
    message_id = models.CharField(max_length=200, default='')
    sent_date = models.CharField(max_length=100, default='')
    cost = models.CharField(max_length=10, default='')
    sender_number = models.CharField(max_length=20)
    


class Profile(models.Model):
    user_id = models.IntegerField(default=0)
    image = ContentTypeRestrictedFileField(_("Avatar"), upload_to=upload_to, content_types=["image/jpeg", "image/jpg", "image/png"], max_upload_size=2621440, blank=True, null=True)
    
    
    
class ProfileUpdater(models.Model):
    user_id = models.IntegerField(default=0)
    update_counter = models.BigIntegerField(default=0) # NOTE - will be updated on successful update process



class Point(models.Model):
    user_id = models.IntegerField(default=0)
    points = models.BigIntegerField(default=0)
    
    
class USSID(models.Model):
    user_id = models.IntegerField(default=0)
    ssid = models.CharField(max_length=20, default='')
    
    
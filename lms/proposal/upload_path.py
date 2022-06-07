import os

from django.utils import timezone
import uuid


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"images/cover/proposals/{uuid.uuid4()}-{now:%Y-%m-%d-%H-%M-%S}{milliseconds}{extension}"



def ckeditor_upload_image_path(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"images/ckeditor/proposals/{uuid.uuid4()}-{now:%Y-%m-%d-%H-%M-%S}{milliseconds}{extension}"


def ckeditor_upload_video_path(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f'videos/ckeditor/proposals/{uuid.uuid4()}-{now:%Y-%m-%d-%H-%M-%S}{milliseconds}{extension}'
import os

from django.utils import timezone
import uuid


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_cert_path(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"certificates/{instance.cert_type}/user_course_id/{instance.user_course_id.id}/{uuid.uuid4()}-{now:%Y-%m-%d-%H-%M-%S}{milliseconds}{extension}"
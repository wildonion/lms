from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from courses.models import User_Course
from .cert_validation import ContentTypeRestrictedFileField
from .upload_path import upload_cert_path
from .utils import cert_number_generator


class Certificate(models.Model):
    cert_type_options = (('Exam', 'exam'), ('Course', 'course'),)
    user_course_id = models.ForeignKey(User_Course, on_delete=models.PROTECT)
    description = models.TextField()
    content = ContentTypeRestrictedFileField(_("Certificate"), upload_to=upload_cert_path, content_types=["application/pdf"], max_upload_size=5242880, blank=True, null=True)
    issued_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(auto_now=True)
    c_number = models.CharField(max_length=10, default=cert_number_generator())
    cert_type = models.CharField(max_length=150, choices=cert_type_options, default='course')








import datetime
import jwt
from django.conf import settings
from django.db.models import ImageField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _





class ContentTypeRestrictedFileField(ImageField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 0)
        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)
    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass
        return data







def generate_access_token(user):
    access_token_payload = {
        # 'username': user["username"],
        'user_id': user["user_id"],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token






def generate_refresh_token(user):
    refresh_token_payload = {
        # 'username': user["username"],
        'user_id': user["user_id"],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256')
    return refresh_token






def decode_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except jwt.DecodeError:
        payload = "decode error"
    except jwt.ExpiredSignatureError:
        payload = "expired"
    return payload
    
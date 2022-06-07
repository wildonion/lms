from django.core.exceptions import ValidationError



def video_content_type_validator(self):
    allowed_extensions = ['video/x-msvideo', 'video/MOV', 'video/avi', 'video/mp4', 'video/webm', 'video/mkv',
                          'video/WMV', 'video/FLV', ]
    if self.content_type not in allowed_extensions:
        raise ValidationError('File type is not supported')



def video_size_validator(self):
    limit_in_MB = 2000
    limit = limit_in_MB * 1024 * 1024
    if self.size > limit:
        raise ValidationError(
            f'your file is {round(self.size / 1024 / 1024)} Mb. Size should not exceed {limit_in_MB} MiB.')
        # raise ValidationError('File too large. Size should not exceed 100 MiB.')

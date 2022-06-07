from django.core.exceptions import ValidationError



def image_size_validator(self):
    limit_in_MB = 5
    limit = limit_in_MB * 1024 * 1024
    if self.size > limit:
        raise ValidationError(
            f'your file is {round(self.size / 1024 / 1024)} Mb. Size should not exceed {limit_in_MB} MiB.')

    # def image_content_type_validator(self):
    #     allowed_extensions = ['image/bmp', 'image/jpeg', 'image/jpeg', 'image/tiff', ]
    #     print(f'type = {self.content_type}')
    #     if self.content_type not in allowed_extensions:
    #         raise ValidationError('File type is not supported')

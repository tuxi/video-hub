from rest_framework import serializers
from django.core.exceptions import ValidationError
from .forms import VideoField as DjangoVideoField

class VideoField(serializers.FileField):
    default_error_messages = {
        'invalid_video': (
            'Upload a valid video. The file you uploaded was either not an video or a corrupted video.'
        ),
    }

    def __init__(self, *args, **kwargs):
        self._DjangoVideoField = kwargs.pop('_DjangoVideoField', DjangoVideoField)
        super(VideoField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # Image validation is a bit grungy, so we'll just outright
        # defer to Django's implementation so we don't need to
        # consider it, or treat PIL as a test dependency.
        file_object = super(VideoField, self).to_internal_value(data)
        django_field = self._DjangoVideoField()
        django_field.error_messages = self.error_messages
        django_field.to_python(file_object)
        return file_object


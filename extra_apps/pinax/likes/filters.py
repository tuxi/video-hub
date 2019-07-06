import django_filters

from .models import Like


class LikeFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Like
        fields = ['receiver_content_type', 'sender']
import django_filters

from .models import Message


class MessageFilter(django_filters.rest_framework.FilterSet):
    '''
    根据回话id获取所有聊天内容
    '''
    class Meta:
        model = Message
        fields = ['dialog']
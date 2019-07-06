# -*- coding: utf-8 -*-
# @Time    : 2019/4/7 9:40 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : views.py
# @Software: PyCharm

from rest_framework import mixins
from rest_framework import viewsets, filters
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserHomeSerializer, UserPublishedListSerializer

User = get_user_model()


class UserPublishedListViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    '''
    list:
        用于获取用户发布的动态内容列表
    '''
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserPublishedListSerializer

    def retrieve(self, request, *args, **kwargs):
        return super(UserPublishedListViewSet, self).retrieve(request=request)

class UserHomeListViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    '''
    list:
        用于获取用户发布的动态内容列表
    '''
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserHomeSerializer
    # lookup_field = 'id'


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        dict = serializer.data
        videos = dict.get('videos')
        liking = dict.get('liking')
        segments = []
        if videos != None:
            segments.append(videos)
            del dict['videos']
        if liking != None:
            segments.append(liking)
            del dict['liking']

        new_dict = {
            'user': dict,
            'segments': segments
        }

        return Response(new_dict)


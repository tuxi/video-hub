# -*- coding: utf-8 -*-
# @Time    : 2019/4/7 9:40 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : views.py
# @Software: PyCharm

from rest_framework import mixins
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from utils.permissions import IsOwnerOrReadOnly
from .models import UserFavorite
from .serializers import UserFavoriteDetailSerializer, UserFavoriteSerializer, UserHomeSerializer, UserPublishedListSerializer

User = get_user_model()

class UserFavoriteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    '''
    list:
        获取用户收藏列表
    retrieve:
        判断某个video是否已收藏
    create:
        收藏video
    '''

    # 权限限制，目的是为了只有当前用户才可以操作自己的收藏数据
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    # 用户认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # 设置根据某个字段查找收藏
    lookup_field = 'video_id'

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserFavoriteDetailSerializer
        elif self.action == 'create':
            return UserFavoriteSerializer
        return UserFavoriteSerializer

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

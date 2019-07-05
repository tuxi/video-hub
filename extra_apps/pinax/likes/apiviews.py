from rest_framework import viewsets, permissions, status, authentication, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from pinax.likes.models import Like
from pinax.likes.signals import object_liked, object_unliked
from pinax.likes.utils import widget_context

from utils.permissions import IsOwnerOrReadOnly
from .serializers import LikeCreateSerializer, LikeDetailSerializer


class LikeToggleView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    '''
    list:
        获取用户收藏列表
    retrieve:
        获取某个content是否已收藏
    create:
        收藏 content
    '''
    # 权限限制，目的是为了只有当前用户才可以操作自己的收藏数据
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)
    # 用户认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'list':
            return LikeDetailSerializer
        elif self.action == 'create':
            return LikeCreateSerializer
        return LikeDetailSerializer
    def get_queryset(self):
        likes = Like.objects.all()
        return likes

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data

        content_type_id = serializer.data.get('receiver_content_type')
        content_type = get_object_or_404(ContentType, pk=content_type_id)
        object_id = serializer.data.get('receiver_object_id')
        like = Like.objects.filter(receiver_content_type=content_type, receiver_object_id=object_id)
        object_liked.send(sender=Like, like=like, request=request)

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        list = serializer.data

        return Response(list)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        object_unliked.send(sender=Like, object=instance, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)
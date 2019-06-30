from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from rest_framework import mixins, filters
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication

from video.filters import VideoFilter
from django_filters.rest_framework import DjangoFilterBackend

from video.models import Video, HotSearchWords
from video.serializers import VideoCreateSerializer, VideoDetailSerializer, HotWordsSerializer

from rest_framework_jwt.authentication import JSONWebTokenAuthentication


# 自定义分页
class VideoPagination(PageNumberPagination):
    # 每页的数量
    page_size = 12
    # 客户端可以使用此查询参数控制页面。
    page_query_param = 'page'
    # 客户端可以使用此查询参数控制页面大小。
    page_size_query_param = 'page_size'

    # 置为整数以限制客户端可能请求的最大页面大小。
    max_page_size = 100


class VideoListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    '''
   视频列表页, 分页， 搜索， 过滤， 排序
    '''
    queryset = Video.objects.all()
    serializer_class = VideoDetailSerializer
    # 自定义分页
    pagination_class = VideoPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = VideoFilter
    search_fields = ('content', )
    ordering_fields = ('audit_completed_time', 'click_num', 'view_num', )
    # 配置授权的认证方式为token，配置完成后未登录，无法访问此页面，否则会抛异常，列表页不需要配置
    # authentication_classes = (TokenAuthentication, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class HotSearchsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    '''
    获取热门搜索词列表
    '''
    queryset = HotSearchWords.objects.all().order_by('-index')
    serializer_class = HotWordsSerializer

class VideoViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    '''
    retrieve:
        获取视频详情
    create:
        创建视频
    '''
    queryset = Video.objects.all()

    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return VideoDetailSerializer
        elif self.action == "create":
            return VideoCreateSerializer

        return VideoDetailSerializer
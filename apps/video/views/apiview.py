from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import mixins, filters
from rest_framework import viewsets, authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from video.filters import VideoFilter
from video.models import Video, HotSearchWords
from video.serializers import VideoCreateSerializer, VideoDetailSerializer, HotWordsSerializer
from utils.utils import CustomPagination

User = get_user_model()


class VideotViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    '''
    retrieve:
        根据id获取视频详情
    create:
        创建视频
    list:
        视频列表页, 分页， 搜索， 过滤， 排序
    destory:
        根据id删除视频

    '''
    queryset = Video.objects.all()
    serializer_class = VideoDetailSerializer
    # 自定义分页
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = VideoFilter
    search_fields = ('content', )
    ordering_fields = ('audit_completed_time', 'id', 'upload_time', 'click_num', 'view_num', )
    # 单独在此视图中配置访问权限, 必须登录才能访问，如果登录了，将登录的用户和登录的令牌存在request中
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def retrieve(self, request, *args, **kwargs):
        # 查看详情时，点击数加1
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)



    # 动态加载权限验证
    # def get_permissions(self):
    #
    #     if self.request.method == 'POST' or self.request.method == 'PUT':
    #         self.permission_classes.append(IsOwnerOrReadOnly)
    #     return [auth() for auth in self.authentication_classes]
    #
    #
    def get_authenticators(self):
        return super(VideotViewSet, self).get_authenticators()

    def get_permissions(self):
        if self.action == 'retrieve':
            return []
        elif self.action == 'create':
            # 如果创建视频必须要有权限才可以
            return [permissions.IsAuthenticated()]
        elif self.action == "destory":
            return [permissions.IsAuthenticated()]
        return []


    def get_serializer_class(self):
        if self.action == "retrieve":
            return VideoDetailSerializer
        elif self.action == "create":
            return VideoCreateSerializer

        return VideoDetailSerializer

    def destroy(self, request, *args, **kwargs):
        return super(VideotViewSet, self).destroy(request)

class HotSearchsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    '''
    获取热门搜索词列表
    '''
    queryset = HotSearchWords.objects.all().order_by('-index')
    serializer_class = HotWordsSerializer

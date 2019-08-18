from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, authentication, mixins
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import filters

from django_private_chat.filters import MessageFilter
from django_private_chat.models import Dialog, Message
from utils.utils import CustomPagination
from utils.permissions import IsOwnerOrReadOnly
from django_private_chat.serializers import DialogDetailSerializer, DialogCreateSerializer, MessageDetailSerializer, MessageCreateSerializer


class DialogListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    '''
    retrieve:
        根据dialog id获取会话详情
    create:
        创建会话
    list:
        获取当前用户的所有会话列表, 分页，排序；这条dialog的 owner 和 opponent 是当前用户才可以获取到
    destory:
        根据id删除会话

    '''
    serializer_class = DialogDetailSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    # 自定义分页
    pagination_class = CustomPagination
    ordering_fields = ('modified', 'created')
    # 身份验证, 单独在此视图中配置身份验证, 必须登录才能访问，如果登录了，将登录的用户和登录的令牌存在request中
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_queryset(self):
        dialogs = Dialog.objects.filter(Q(owner=self.request.user) | Q(opponent=self.request.user))
        return dialogs

    # 权限限制
    def get_permissions(self):
        return [permissions.IsAuthenticated()]


    def get_serializer_class(self):
        if self.action == "retrieve":
            return DialogDetailSerializer
        elif self.action == "create":
            return DialogCreateSerializer

        return DialogDetailSerializer

    def destroy(self, request, *args, **kwargs):
        return super(DialogListViewSet, self).destroy(request)



class MessageListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    '''
    create:
        创建message
    list:
        获取当前用户与某个用户的会话的所有消息
    destory:
        根据id删除message

    '''
    serializer_class = MessageDetailSerializer
    # 自定义分页
    pagination_class = CustomPagination

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # 自定义filter 实现根据dialog id获取所有聊天内容
    filter_class = MessageFilter

    # 按照时间排序消息
    ordering_fields = ('created', )

    # 身份验证, 单独在此视图中配置身份验证, 必须登录才能访问，如果登录了，将登录的用户和登录的令牌存在request中
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_queryset(self):
        # 匹配这条消息的发起者或者接受者为当前用户
        messages = Message.objects.filter(Q(dialog__opponent=self.request.user) | Q(dialog__owner=self.request.user))
        return messages

    # 权限限制
    def get_permissions(self):
        return [permissions.IsAuthenticated()]


    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer

        return MessageDetailSerializer

    def destroy(self, request, *args, **kwargs):
        return super(MessageListViewSet, self).destroy(request)


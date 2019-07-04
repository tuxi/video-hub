from random import choice

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework import viewsets, permissions, status, authentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from .serializers import SmsSerializer, UserRegisterSerializer, UserDetailSerializer, UserUpdateSerializer
from utils.yunpian import YunPian
from VideoHub.settings import YUNPIAN_APIKEY
from .models import VerifyCode

# Create your views here.

User = get_user_model()

class CustomBackend(ModelBackend):
    '''
    用于权限验证
    '''
    def authenticate(self, request, mobile=None, username=None, password=None, **kwargs):
        '''
        自定义用户验证
        :param request:
        :param mobile:
        :param password:
        :param kwargs:
        :return:
        '''


        user = None
        # 通过username 或者 mobile 取出用户
        # user = User.objects.get(Q(mobile=mobile) | Q(username=username))

        if username != None:
            try:
                user = User.objects.get(Q(username=username))
            except Exception as e:
                pass
        if mobile != None:
            try:
                user = User.objects.get(Q(mobile=mobile))
            except Exception as e:
                pass

        if user != None and user.check_password(password):
            return user

class SmsCodeViewSet(CreateModelMixin, viewsets.GenericViewSet):
    '''
    发送短信验证码：
    '''

    serializer_class = SmsSerializer

    def generate_code(self):
        '''
        随机生成四位数字的验证码
        :return:
        '''
        seeds = '0123456789'
        randoms_str = []

        for i in range(4):
            randoms_str.append(choice(seeds))
        return "".join(randoms_str)

    # 重载父类CreateModelMixin的方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 取出mobile
        mobile = serializer.validated_data['mobile']

        yunpian = YunPian(YUNPIAN_APIKEY)
        code = self.generate_code()
        sms_status = yunpian.send_sms(code, mobile)

        if sms_status['code'] != 0:
            return Response(
                {
                    "mobile": sms_status["msg"]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # 将验证码存储到数据库
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response(
                {
                    'mobile': mobile
                },
                status=status.HTTP_201_CREATED
            )

class UserViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    '''
    retrieve:
        获取用户详情
    create:
        注册用户
    update:
        修改用户
    '''
    #serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegisterSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            # 部分更新
            return UserUpdateSerializer

        return UserDetailSerializer


    def retrieve(self, request, *args, **kwargs):
        return super(UserViewSet, self).retrieve(request=request)

    def get_authenticators(self):
        return super(UserViewSet, self).get_authenticators()



    def get_permissions(self):
        # 动态加载权限验证
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return []
        elif self.action == 'update' or self.action == 'partial_update':
            return [permissions.IsAuthenticated()]
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # 通过user 生成 token
        # re_dict = serializer.data
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # re_dict['name'] = user.name if user.name else user.username

        # 自定义创建用户成功时返回的数据结构
        dict = {
            'token': token,
            'user': UserDetailSerializer(user, context={'request': request}).data,
            # 'user': re_dict,
        }

        headers = self.get_success_headers(serializer.data)
        return Response(dict, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        # 修改完用户信息后返回完整的用户序列化数据
        dict = UserDetailSerializer(instance, context={'request': request}).data
        return Response(dict)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        # 重载此方法 返回user
        return serializer.save()



def jwt_response_payload_handler(token, user=None, request=None):
   """
   登录成功后自定义返回
   :param token:
   :param user:
   :param request:
   :return:
   """
   dict = {
       "token": token,
       'user': UserDetailSerializer(user, context={'request': request}).data
   }
   return dict
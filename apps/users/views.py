from random import choice

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework import viewsets, permissions, status, authentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from .serializers import SmsSerializer, UserRegisterSerializer, UserDetailSerializer
from utils.yunpian import YunPian
from VideoHub.settings import YUNPIAN_APIKEY
from .models import VerifyCode

# Create your views here.

User = get_user_model()

class CustomBackend(ModelBackend):
    '''
    用于权限验证
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        自定义用户验证
        :param request:
        :param username:
        :param password:
        :param kwargs:
        :return:
        '''
        try:
            # 通过username 或者 mobile 取出用户
            user = User.objects.get(Q(username=username)|Q(mobile =username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None

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

        return UserDetailSerializer



    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return []
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # 通过user 生成 token
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['name'] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

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
        "code":2000,
        "data": {
            "token": token,
            'user': UserDetailSerializer(user, context={'request': request}).data
        }
   }
   return dict
# -*- coding: utf-8 -*-
# @Time    : 2019/4/5 9:52 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : serializers.py
# @Software: PyCharm

from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

from .models import VerifyCode

User = get_user_model()

class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        '''
        验证手机号码
        :param mobile:
        :return:
        '''

        # 手机号是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")

        # 手机号码是否合法
        from VideoHub.settings import REGEX_MOBILE
        import re
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号非法")

        # 验证码发送的频率 1分钟只能发一个
        one_minters_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minters_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60秒")

        return mobile

class UserDetailSerializer(serializers.ModelSerializer):
    '''
    用户详情序列化
    '''
    class Meta:
        model = User
        fields = ('name', 'gender', 'birthday', 'email', 'mobile')

class UserRegisterSerializer(serializers.ModelSerializer):
    '''
    用户注册序列化
    '''
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    # 将mobile设置非必填，是为了适配前端在请求时只传入username，而未传入mobile时的问题，在本后端，username为mobile，mobile也是username，是唯一的
    # 在user的models中UserProfile的设置了mobile可以为null或blank，这里就不需要设置了
    # mobile = serializers.CharField(label='手机号', help_text='手机号', required=False)

    # def create(self, validated_data):
          # 重载父类方法，为了将密码以密文的方式保存到数据库
    #     users = super(UserRegSerializer, self).create(validated_data=validated_data)
    #     users.set_password(validated_data["password"])
    #     users.save()
    #     return users

    def validate_code(self, code):
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)
        # except VerifyCode.DoesNotExist as e:
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["mobile"]).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]

            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")

        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        '''
        判断完毕后删除验证码，因为没有什么用了
        这个方法运用在modelserializer中，可以剔除掉write_only的字段，这个字段只验证，但不存在于指定的model当中，即不能save( )，可以在这delete掉；例如短信验证码验证完毕后就可以删除了：
        :param attrs:
        :return:
        '''
        if "mobile" not in attrs:
            attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")



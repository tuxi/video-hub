# -*- coding: utf-8 -*-
# @Time    : 2019/4/7 9:40 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

from .models import UserFavorite
from video.serializers import VideoDetailNoUserSerializer

User = get_user_model()


class UserFavoriteSerializer(serializers.ModelSerializer):

    # 让user是隐藏字段
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserFavorite

        validators = [
            # 设置联合唯一
            UniqueTogetherValidator(
                queryset=UserFavorite.objects.all(),
                fields=('user', 'video'),
                message="已经收藏"
            )
        ]

        fields = ("user", "video", "id")

class UserFavoriteDetailSerializer(serializers.ModelSerializer):
    # 序列化video
    video = VideoDetailNoUserSerializer(many=True)

    class Meta:
        model = UserFavorite
        # 将序列化的video放到收藏详情字段中
        fields = ("video", "id")

class UserPublishedListSerializer(serializers.ModelSerializer):
    videos = VideoDetailNoUserSerializer(many=True)
    class Meta:
        model = User
        fields = (
        'id', 'nickname', 'username', 'gender', 'birthday', 'email', 'mobile', 'avatar', 'head_background', 'website',
        'summary', 'videos')
# -*- coding: utf-8 -*-
# @Time    : 2019/4/7 9:40 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers
from django.contrib.auth import get_user_model

from video.serializers import VideoDetailNoUserSerializer, VideoDetailSerializer
from pinax.likes.models import Like
from video.models import Video

User = get_user_model()


class UserPublishedListSerializer(serializers.ModelSerializer):
    videos = VideoDetailSerializer(many=True)
    class Meta:
        model = User
        fields = (
        'id', 'nickname', 'username', 'gender', 'birthday', 'email', 'mobile', 'avatar', 'head_background', 'website',
        'summary', 'videos')

class UserHomeSerializer(serializers.ModelSerializer):
    # videos = VideoDetailSerializer(many=True)
    # liking = LikeDetailSerializer(many=True)
    videos = serializers.SerializerMethodField()
    liking = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id', 'nickname', 'username', 'gender', 'birthday', 'email', 'mobile', 'avatar', 'head_background',
            'website',
            'summary', 'videos', 'liking')

    def get_liking(self, user):
        '''
        请求用户喜欢的视频, 这里不返回视频数据，只返回视频数量
        :param user:
        :return:
        '''

        # 这里不查询liking字段了，因为它在客户端首页第二个类别，只有用户主动请求才展示，直接返回这个字段用告知客户端有这一项，如果linking需要一并返回，请使用liking = LikeDetailSerializer(many=True)
        queryset = Like.objects.filter(sender=user, receiver_content_type=6).order_by('-timestamp')
        total = len(queryset)
        return {
            "title": "喜欢",
            'data': [],
            'total': total, # 总数
            'nextpage': 0,
            'category': 'liking'
        }

    def get_videos(self, user):
        '''
        请求用户发布的视频, 最多返回前20条
        :param user:
        :return:
        '''
        # 根据user查找它的视频, 按照upload_time降序, 查找前20个视频
        queryset = Video.objects.filter(user=user).order_by('-upload_time')
        count = len(queryset)
        list = queryset[:20]

        jsonList = []
        for video in list:
            # 必须要把context带过去，不然此序列化会导致缺少request，序列化的url不是完整的地址
           jsonList.append(VideoDetailSerializer(instance=video, context=self.context).data)
        return {
            "title": "作品",
            'data': jsonList,
            'total': count, # 总数
            'nextpage': 1,
            'category': 'videos'
        }
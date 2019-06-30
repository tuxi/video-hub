# -*- coding: utf-8 -*-
# @Time    : 2019/3/17 2:49 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers
from .models import Video, VideoCategory, HotSearchWords
import os
from videokit.serializers import VideoField


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = VideoCategory
        fields = '__all__'

class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = VideoCategory
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    # sub_cat 为related_name 指定的， parent_category = models.ForeignKey("self", null=True, blank=True, verbose_name="父类级别", help_text="父类目", related_name="sub_cat")
    sub_cat = CategorySerializer2(many=True)
    class Meta:
        model = VideoCategory
        fields = '__all__'


# 通过继承serializers.ModelSerializer 序列化，不用手动添加，可自动序列化全部字段，或者一部分字段
class GoodsSerializer(serializers.ModelSerializer):
    # 序列化时，如果存在ForeignKey这样的字段，比如category，默认序列化的是id，如果要序列化这个ForeignKey对于的model，则需要重载对应的字段，这样这个字段会根据其CategorySerializer嵌入到序列化中
    category = CategorySerializer()
    class Meta:
        model = Video
        # 序列化全部字段
        fields = '__all__'
        # 也可以设置部分需要序列化的字段
        #fields = ('market_price', 'name')


class HotWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = '__all__'


class VideoDetailSerializer(serializers.ModelSerializer):
    '''
    视频详情序列化
    '''
    class Meta:
        model = Video
        fields = '__all__'


class VideoCreateSerializer(serializers.ModelSerializer):
    '''
    创建视频序列化 并对这些字段的验证
    '''

    content = serializers.CharField(required=True, max_length=200, min_length=1, label="视频描述",
                                 error_messages={
                                     "blank": "请输入视频描述",
                                     "required": "请输入视频描述",
                                     "max_length": "视频描述的内容最多200字",
                                     "min_length": "视频描述的内容最少1字"
                                 },
                                 help_text="视频描述")

    cover_duration = serializers.IntegerField(required=False, label="视频动态封面播放的秒数", max_value=10, min_value=3,help_text="视频动态封面播放的秒数",
                                              error_messages={
                                                  'max_value': '封面时间最长10秒',
                                                  'min_value': '封面时间最小3秒',
                                              },
                                              )
    cover_start_second = serializers.IntegerField(required=False, label="封面的起始时间", min_value=0, help_text="封面的起始时间")

    video = VideoField(required=True, label="视频文件")

    longitude = serializers.FloatField(required=False, label="经度")
    latitude = serializers.FloatField(required=False, label="纬度")
    poi_name = serializers.CharField(required=False, label="poi的名称")
    poi_address = serializers.CharField(required=False, label="poi地址")

    first_create_time = serializers.DateTimeField(required=True, label="视频首次在本地创建的时间")

    source = serializers.SerializerMethodField()


    def fix_video_file_name(self, video_file):
        '''
        解决上传的文件名太长问题
        :param video_file:
        :return:
        '''

        nameExtension = os.path.splitext(video_file.name)[1]
        from utils.utils import create_md5

        hash = create_md5()

        # startswith中拥有多个参数必须是元组形式，只需满足一个条件，返回True
        if nameExtension.startswith((".",)):
            file_name = hash + nameExtension
        else:
            file_name = hash + '.' + nameExtension
        video_file.name = file_name

    def create(self, validated_data):
        '''
        重载父类方法，为了将处理视频及其封面并保存到本地
        :param validated_data:
        :return:
        '''
        # 请求的用户
        user = self.context['request'].user
        # 请求的参数username
        user_id = user.id
        if user_id == None:
            user_id = 1
        validated_data["user_id"] = user_id

        self.fix_video_file_name(validated_data["video"])

        # 创建对象 此方法会调用model的save()方法保存到数据
        videoItem = super(VideoCreateSerializer, self).create(validated_data=validated_data)

        return videoItem



    class Meta:
        model = Video
        # 注册用户时需要post的字段
        fields = ("content", "cover_duration", "cover_start_second", "video", "longitude", "latitude" , "poi_name", "poi_address", "first_create_time", "source")




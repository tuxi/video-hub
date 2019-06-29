# -*- coding: utf-8 -*-
# @Time    : 2019/3/17 2:49 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers
from .models import Video, VideoCategory, HotSearchWords


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
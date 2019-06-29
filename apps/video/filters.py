# -*- coding: utf-8 -*-
# @Time    : 2019/3/18 10:19 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django.db.models import Q
from .models import Video

class VideoFilter(django_filters.rest_framework.FilterSet):
    '''
    视频过滤类
    '''
    begin_time = django_filters.NumberFilter(name='audit_completed_time', help_text="起始时间", lookup_expr='gte')
    end_time = django_filters.NumberFilter(name='audit_completed_time', help_text='结束时间', lookup_expr='lte')

    # 自定义过滤，过滤的方法为top_category_filter
    top_category = django_filters.NumberFilter(method='top_category_filter')
    def top_category_filter(self, queryset, name, value):
        '''
        找到某一类的所有数据
        :param queryset:
        :param name:
        :param value:
        :return:
        '''
        res = queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value))
        return res

    class Meta:
        model = Video
        fields = ['begin_time', 'end_time', 'is_hot']
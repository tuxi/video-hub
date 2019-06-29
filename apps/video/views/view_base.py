# -*- coding: utf-8 -*-
# @Time    : 2019/3/17 12:49 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : views_base.py
# @Software: PyCharm

from django.views.generic.base import View
from video.models import Video

class VideoListView(View):
    def get(self, request):
        '''
        通过django的view实现列表页
        :param request:
        :return:
        '''

        # 取出数据库中前十个video
        videos = Video.objects.all()[:10]

        # 通过serializers序列化json
        from django.core import serializers
        import json
        json_data = serializers.serialize('json', videos)
        json_list = json.loads(json_data)

        from django.http import JsonResponse
        return JsonResponse(json_list, safe=False)
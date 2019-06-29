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

        json_list = []
        # 取出数据库中前十个video
        videos = Video.objects.all()[:10]

        # 手动将models转换为json
        # for video in videos:
        #     json_dict = {}
        #     json_dict["name"] = video.name
        #     json_dict["category"] = video.category.name
        #     json_dict["market_price"] = video.market_price
        #     json_list.append(json_dict)

        # 通过model_to_dict将model转换为json
        # 这里会遇到问题，将model中所以的字段转换为json，导致TypeError: Object of type 'ImageFieldFile' is not JSON serializable
        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)

        # 通过serializers序列化json
        from django.core import serializers
        import json
        json_data = serializers.serialize('json', videos)
        json_data = json.loads(json_data)

        from django.http import JsonResponse
        return JsonResponse(json_data, safe=False)
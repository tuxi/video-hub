# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 10:01 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : models.py
# @Software: PyCharm

from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from video.models import Video

User = get_user_model()

class UserFavorite(models.Model):
    """
    用户收藏
    """
    user = models.ForeignKey(User, verbose_name="用户")
    video = models.ForeignKey(Video, verbose_name="视频", help_text="视频id")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        # 设置联合唯一的字段，只允许某个用户对同一商品收藏一次
        unique_together = ("user", "video")

    def __str__(self):
        return self.user.username




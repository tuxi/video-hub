# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 10:01 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : adminx.py
# @Software: PyCharm

import xadmin
from .models import UserFavorite


class UserFavoriteAdmin(object):
    list_display = ['user', 'video', "add_time"]



xadmin.site.register(UserFavorite, UserFavoriteAdmin)
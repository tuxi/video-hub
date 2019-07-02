# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 10:01 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : apps.py
# @Software: PyCharm

from django.apps import AppConfig


class UserOperationConfig(AppConfig):
    name = 'user_operation'
    verbose_name = "用户操作管理"

    def ready(self):
        import user_operation.signals
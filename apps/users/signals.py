# -*- coding: utf-8 -*-
# @Time    : 2019/4/6 10:46 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : signals.py
# @Software: PyCharm

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

# @receiver(post_save, sender=User)
# def create_user(sender, instance=None, created=False, **kwargs):
#     '''
#     接收创建用户的信号，将密码改为密文保存到数据库
#     :param sender:
#     :param instance:
#     :param created:
#     :param kwargs:
#     :return:
#     '''
#     if created:
#         password = instance.password
#         # 这里导致`createsuperuser`创建用户时密码二次被编码，而登录时对密码进行解码时出错
#         instance.set_password(password)
#         instance.save()
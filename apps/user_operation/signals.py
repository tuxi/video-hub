# -*- coding: utf-8 -*-
# @Time    : 2019/4/11 10:05 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : signals.py
# @Software: PyCharm

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


from user_operation.models import UserFavorite


@receiver(post_save, sender=UserFavorite)
def create_userfav(sender, instance=None, created=False, **kwargs):
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(post_delete, sender=UserFavorite)
def delete_userfav(sender, instance=None, created=False, **kwargs):
    goods = instance.goods
    goods.fav_num -= 1
    goods.save()

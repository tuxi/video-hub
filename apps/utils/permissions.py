# -*- coding: utf-8 -*-
# @Time    : 2019/4/7 9:34 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : permissions.py
# @Software: PyCharm
# 权限设置

from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
       Object-level permission to only allow owners of an object to edit it.
       Assumes the model instance has an `owner` attribute.
       """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user

    def has_permission(self, request, view):
        try:
            user = request.user
            if isinstance(user, User):
                return True
        except Exception as e:
            print(e)
            return False
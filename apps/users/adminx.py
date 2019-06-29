# -*- coding: utf-8 -*-
# @Time    : 2019/4/6 10:53 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : adminx.py
# @Software: PyCharm

import xadmin
from xadmin import views
from .models import VerifyCode

# 注册主题
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True
xadmin.site.register(views.BaseAdminView, BaseSetting)

class GlobalSettings(object):
    site_title = "北京恩巴网络技术有限公司"
    site_footer = "enba.com"
    menu_style = "accordion"  # 选项卡折叠效果

class VerifyCodeAdmin(object):
    list_display = ['code', 'mobile', "add_time"]

xadmin.site.register(VerifyCode, VerifyCodeAdmin)
xadmin.site.register(views.CommAdminView, GlobalSettings)

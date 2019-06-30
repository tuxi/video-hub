from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UserProfile(AbstractUser):
    '''
    用户
    注意：UserProfile设计完成后，并没有真正的替换系统用户，还需要在settings.py中设置 AUTH_USER_MODEL = 'users.UserProfile'
    '''

    # 用户姓名，由于本用户系统是以手机号注册为基础的，所以在最初时用户姓名不需要填
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    # 出生年月日
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月日")
    # 性别 默认为女
    gender = models.CharField(max_length=6, choices=(('male', u'男'), ('female', u'女')), default='famle')
    # 手机号
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="手机号")
    # 邮箱
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")
    avatar = models.ImageField(upload_to="user/avatar/image/%Y/%m", null=True, blank=True, verbose_name="头像",
                               help_text="头像")
    headbackground = models.ImageField(upload_to="user/headbackground/image/%Y/%m", null=True, blank=True, verbose_name="个人中心的头部背景",
                               help_text="个人中心的头部背景")

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class VerifyCode(models.Model):
    '''
    短信验证码
    保存手机号登录时请求的验证码，用于请求后，验证的
    也可以将验证码保存到内存中的，但是这里为了方便理解，将其保存到数据库
    '''
    code = models.CharField(max_length=10, verbose_name='验证码')
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "短信验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code


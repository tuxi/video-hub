# -*- coding: utf-8 -*-
# @Time    : 2019/6/29 12:06 AM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : __init__.py.py
# @Software: PyCharm

import hashlib

from django.db import models
from django.utils import timezone as datetime

from videokit.models import VideoField
from django.contrib.auth import get_user_model

User = get_user_model()


def upload_to(instance, filename):
    return 'media_items{filename}'.format(filename=filename)

class Video(models.Model):
    """
    媒体文件
    """
    STATUS_CHOICES = (
        ('d', '审核通过'),
        ('p', '发布'),
    )

    # 视频来源
    VIDEO_SOURCE = (
        ('c', '相机'),
        ('a', '相册')
    )

    video = VideoField(upload_to=upload_to,
                       width_field='video_width', height_field='video_height',
                       rotation_field='video_rotation',
                       mimetype_field='video_mimetype',
                       duration_field='video_duration',
                       thumbnail_field='video_cover_image',
                       animated_webp_field='video_animated_webp',
                       # gif_field='video_gif',
                       mp4_field='video_mp4',
                       # aac_field='video_sound',
                       cover_duration_filed='cover_duration',
                       cover_start_second_filed='cover_start_second')
    video_width = models.IntegerField(null=True, blank=True, verbose_name="视频的宽度")
    video_height = models.IntegerField(null=True, blank=True, verbose_name="视频的高度")
    video_rotation = models.FloatField(null=True, blank=True, verbose_name="视频的旋转")
    video_mimetype = models.CharField(max_length=32, null=True, blank=True, verbose_name="视频的类型")
    # 视频时长
    video_duration = models.IntegerField(null=True, blank=True, verbose_name="视频的时长")
    # 视频的封面
    video_cover_image = models.ImageField(null=True, blank=True, verbose_name="视频的封面")
    # 视频前3秒的gif图
    # video_gif = models.ImageField(null=True, blank=True)
    # mp4 类型的视频文件
    video_mp4 = models.FileField(blank=True, null=True, verbose_name="mp4 类型的视频文件")
    # video_sound = models.FileField(blank=True, verbose_name='sound', null=True)

    # 视频前10秒的wep动图，和gif的功能基本相同，使用webp是为了优化客户端流量及性能
    video_animated_webp = models.ImageField(null=True, blank=True, verbose_name="视频前10秒的wep动图")
    # 封面的起始时间，决定webp从视频的哪里开始显示
    cover_start_second = models.FloatField(default=0, null=True, blank=True, verbose_name="封面的起始时间")
    # 封面的长度，决定webp的播放时间, 默认5秒
    cover_duration = models.FloatField(default=5, null=True, blank=True, verbose_name="封面的长度，决定webp的播放时间")
    # 视频上传的时间
    upload_time = models.DateTimeField(default=datetime.now, verbose_name="视频上传的时间")
    # 视频首次在本地创建的时间
    first_create_time = models.DateTimeField(default=datetime.now, verbose_name="视频首次在本地创建的时间")
    # 视频审核完成时间，此时间由服务端控制
    audit_completed_time = models.DateTimeField(blank=True, null=True, verbose_name="视频审核完成时间，此时间由服务端控制")
    # 视频观看次数
    view_num = models.PositiveIntegerField(default=0, verbose_name="视频观看次数")
    click_num = models.IntegerField(default=0, verbose_name="点击数", help_text="点击数")
    # on_delete指定外键的删除 CASCADE, related_name 给这个外键定义好一个别的名称
    user = models.ForeignKey(User, related_name='videos', verbose_name='用户', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p', verbose_name='视频状态',)

    content = models.CharField(max_length=200, unique=False, verbose_name="标题")
    # tags = models.ManyToManyField(VideoTag, through="PostTag", through_fields=('post', 'tag'))
    is_hot = models.BooleanField(default=False, verbose_name="是否hot")

    is_active = models.BooleanField(default=True, verbose_name="是否激活", help_text="是否激活")
    is_commentable = models.BooleanField(default=True, verbose_name="是否可评论", help_text="是否可评论")

    # 经度
    longitude = models.FloatField(null=False, blank=False, verbose_name="经度")
    # 纬度
    latitude = models.FloatField(null=False, blank=False, verbose_name="纬度")
    poi_name = models.CharField(max_length=200, unique=False, null=False, blank=False, verbose_name="poi本地化名称")
    poi_address = models.CharField(max_length=300, unique=False, null=False, blank=False, verbose_name='poi地址')

    source = models.CharField(max_length=1, choices=VIDEO_SOURCE, default='c', verbose_name="视频来源")

    # browse_password = models.CharField(max_length=20, null=True, blank=True, verbose_name="浏览密码", help_text="浏览密码")
    # browse_password_encrypt = models.CharField(max_length=100, null=True, blank=True, verbose_name="浏览密码加密",
    #                                            help_text="浏览密码加密")

    def save(self, *args, **kwargs):
        # if self.browse_password and len(self.browse_password) > 0:
        #     md5 = hashlib.md5()
        #     md5.update(self.browse_password.encode('utf8'))
        #     self.browse_password_encrypt = md5.hexdigest()
        # else:
        #     self.browse_password_encrypt = None

        if self.audit_completed_time == None:
            self.audit_completed_time = datetime.now()
        super(Video, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

class HotSearchWords(models.Model):
    """
    热搜词
    """
    keywords = models.CharField(default="", max_length=20, verbose_name="热搜词")
    index = models.IntegerField(default=0, verbose_name="排序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = '热搜词'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.keywords

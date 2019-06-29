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

class VideoCategory(models.Model):
    '''
    video category
    '''

    CATEGORY_LEVEL = (
        ("1", "一级类目"),
        ("2", "二级类目"),
        ("3", "三级类目")
    )

    name = models.CharField(max_length=30, default="", verbose_name="类别名", help_text="类别名")
    category_type = models.CharField(max_length=30, choices=CATEGORY_LEVEL, verbose_name="路由编码", help_text="用于配置路由跳转")
    desc = models.TextField(null=True, blank=True, verbose_name="类别描述", help_text="类别描述")
    image = models.ImageField(upload_to="comment/category/image/%Y/%m", null=True, blank=True, help_text="图片")
    category_level = models.CharField(max_length=20, choices=CATEGORY_LEVEL, verbose_name="类目级别", help_text="类目级别")
    parent_category = models.ForeignKey("self", null=True, blank=True, verbose_name="父类目级别", help_text="父目录",
                                        related_name="sub_category")
    is_active = models.BooleanField(default=True, verbose_name="是否激活", help_text="是否激活")
    is_tab = models.BooleanField(default=True, verbose_name="是否导航", help_text="是否导航")
    index = models.IntegerField(default=0, verbose_name="排序", help_text="排序")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    def save(self, *args, **kwargs):
        # 为英文标题和简介提供默认值
        # if not self.en_name:
        #     self.en_name = self.name
        # if not self.en_desc:
        #     self.en_desc = self.desc
        super(VideoCategory, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name + '列表'

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.name, self.get_category_type_display(), self.get_category_level_display())

class LocationItem(models.Model):
    #经度
    longitude = models.FloatField(null=False, blank=False)
    #纬度
    latitude = models.FloatField(null=False, blank=False)
    name = models.CharField('poi本地化名称', max_length=200, unique=False)
    address = models.CharField('poi地址', max_length=300, unique=False)

    def __str__(self):
        return self.name + self.address

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

    video = VideoField(upload_to=upload_to,
                       width_field='video_width', height_field='video_height',
                       rotation_field='video_rotation',
                       mimetype_field='video_mimetype',
                       duration_field='video_duration',
                       thumbnail_field='video_thumbnail',
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
    cover_start_second = models.FloatField(null=True, blank=True, verbose_name="封面的起始时间")
    # 封面的长度，决定webp的播放时间
    cover_duration = models.FloatField(null=True, blank=True, verbose_name="封面的长度，决定webp的播放时间")
    # 视频上传的时间
    upload_time = models.DateTimeField('上传时间', default=datetime.now, verbose_name="视频上传的时间")
    # 视频首次添加时间
    first_add_time = models.DateTimeField(default=datetime.now, verbose_name="视频首次添加时间")
    # 视频审核完成时间，此时间由服务端控制
    audit_completed_time = models.DateTimeField('发布时间', blank=True, null=True, verbose_name="视频审核完成时间，此时间由服务端控制")
    # 视频观看次数
    view_num = models.PositiveIntegerField(default=0, verbose_name="视频观看次数")
    click_num = models.IntegerField(default=0, verbose_name="点击数", help_text="点击数")
    # user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p', verbose_name='视频状态',)
    location = models.ForeignKey(LocationItem, verbose_name='所在位置', on_delete=models.CASCADE, null=True, blank=True)
    content = models.CharField(max_length=200, unique=False, verbose_name="标题")
    category = models.ForeignKey(VideoCategory, verbose_name="video category", blank=True, null=True, on_delete=models.CASCADE)
    is_hot = models.BooleanField(default=False, verbose_name="是否hot")

    is_active = models.BooleanField(default=True, verbose_name="是否激活", help_text="是否激活")
    is_commentable = models.BooleanField(default=True, verbose_name="是否可评论", help_text="是否可评论")
    # browse_password = models.CharField(max_length=20, null=True, blank=True, verbose_name="浏览密码", help_text="浏览密码")
    # browse_password_encrypt = models.CharField(max_length=100, null=True, blank=True, verbose_name="浏览密码加密",
    #                                            help_text="浏览密码加密")

    # def save(self, *args, **kwargs):
    #     if self.browse_password and len(self.browse_password) > 0:
    #         md5 = hashlib.md5()
    #         md5.update(self.browse_password.encode('utf8'))
    #         self.browse_password_encrypt = md5.hexdigest()
    #     else:
    #         self.browse_password_encrypt = None
    #     super(Video, self).save(*args, **kwargs)
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

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth import get_user_model

User = get_user_model()

@python_2_unicode_compatible
class Like(models.Model):
    # 定义是谁点的赞
    sender = models.ForeignKey(User, related_name="liking", on_delete=models.CASCADE, verbose_name='点赞的用户')
    # 设定一个普通外键，连接于ContentType，一般名字叫“content_type”。这个字段实际上是代码你在Likes这个点赞里面，是给哪个对应的模型在点赞，是文章/评论/视频，或是其他
    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='content_type',
                                     verbose_name='点赞的模型类型, 关联的表名称')
    # 设立一个PostiveIntegerField的字段，一般名字叫做“object_id”.以记录所对应的模型的实例的id号，比如我们给一篇文章点赞，这篇文章是Post类里的id为10的文章，那么这个object_id就是这个10。
    receiver_object_id = models.PositiveIntegerField(verbose_name='点赞的模型id')
    # 这个外键需要传入两个参数content_type和object_id, #通过找到content_type 找到 关联的表名, object_id 找到行id
    receiver = GenericForeignKey(
        ct_field="receiver_content_type",
        fk_field="receiver_object_id"
    )

    timestamp = models.DateTimeField(default=timezone.now, verbose_name='赞的时间')

    class Meta:
        unique_together = (
            ("sender", "receiver_content_type", "receiver_object_id"),
        )

    def __str__(self):
        return "{0} likes {1}".format(self.sender, self.receiver)


    @classmethod
    def like(cls, sender, content_type, object_id):
        obj, liked = cls.objects.get_or_create(
            sender=sender,
            receiver_content_type=content_type,
            receiver_object_id=object_id
        )
        if not liked:
            obj.delete()
        return obj, liked


from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model
from video.serializers import VideoDetailSerializer

from .models import Like

User = get_user_model()

class LikeCreateSerializer(serializers.ModelSerializer):

    # 让user是隐藏字段
    sender = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Like

        validators = [
            # 设置联合唯一
            UniqueTogetherValidator(
                queryset=Like.objects.all(),
                fields=("sender", "receiver_content_type", "receiver_object_id"),
                message="已经收藏"
            )
        ]

        fields = ("sender", "receiver_content_type", "receiver_object_id", 'id')
        # read_only_fields = ('id',)


class LikeDetailSerializer(serializers.ModelSerializer):
    '''
     序列化收藏的详情
    '''
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = Like
        # 将序列化的video放到收藏详情字段中
        fields = ("receiver_content_type", "receiver_object_id", "timestamp", 'id', 'receiver')

    def get_receiver(self, like):
        obj = like.receiver_content_type.get_object_for_this_type(pk=like.receiver_object_id)
        if like.receiver_content_type.app_label == 'video': # video
            # 在提供序列化器对象的时候，REST framework会向对象的context属性补充三个数据：request、format、view，这三个数据对象可以在定义序列化器时使用。
            serializer = VideoDetailSerializer(instance=obj, context=self.context)
            return serializer.data
        return {}
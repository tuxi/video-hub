from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model
from video.serializers import VideoDetailSerializer
from video.models import Video

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

        fields = ("sender", "receiver_content_type", "receiver_object_id")
        read_only_fields = ('id',)


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
            serializer = VideoDetailSerializer(instance=obj)
            return serializer.data
        return {}
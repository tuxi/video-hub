from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserDetailSerializer
from .models import Dialog, Message


class DialogDetailSerializer(serializers.ModelSerializer):
    '''
    Dialog详情序列化
    '''

    # 序列化时，如果存在ForeignKey这样的字段，比如user，默认序列化的是id，如果要序列化这个ForeignKey对于的model，则需要重载对应的字段，这样这个字段会根据其UserDetailSerializer嵌入到序列化中
    owner = UserDetailSerializer()
    opponent = UserDetailSerializer()

    modified = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()


    class Meta:
        model = Dialog
        fields = ('id', 'owner', 'opponent', 'created', 'modified')

    def get_created(self, instance):

        return instance.get_formatted_create_datetime()

    def get_modified(self, instance):
        return instance.get_formatted_modify_datetime()

class DialogCreateSerializer(serializers.ModelSerializer):
    '''
    创建对话
    '''
    # 让user是隐藏字段, user字段不需要前端直接传递，从requst中就可以拿到授权的user，最终与video关联起来
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    validators = [
        # 设置联合唯一
        UniqueTogetherValidator(
            queryset=Dialog.objects.all(),
            fields=("owner", "opponent"),
            message="聊天会话已存在"
        )
    ]

    class Meta:
        model = Dialog
        fields = ('owner', 'opponent')


class MessageDetailSerializer(serializers.ModelSerializer):
    '''
    一个聊天消息内容，暂时只支持文本
    '''

    created = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('sender', 'text', 'read', 'is_removed', 'created', 'id')

    def get_created(self, instance):

        return instance.get_formatted_create_datetime()


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('dialog', 'sender', 'text')
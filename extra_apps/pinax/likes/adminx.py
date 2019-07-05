import xadmin
from .models import Like

class LikeAdmin(object):
    list_display = ["sender", "receiver_content_type", "receiver_object_id", "timestamp", 'id']



xadmin.site.register(Like, LikeAdmin)

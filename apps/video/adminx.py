import xadmin
from .models import Video, HotSearchWords

class VideoAdmin(object):
    list_display = ["content", "cover_duration", "cover_start_second", "video", "longitude", "latitude" , "poi_name", "poi_address", "first_create_time", "source"]
    search_fields = ['content', ]
    list_editable = ["is_hot", ]
    list_filter = ["content", "click_num", "is_hot", "first_create_time", "upload_time"]
    style_fields = {"content": "ueditor"}


class HotSearchAdmin(object):
    list_display = ["keywords", "index", "add_time"]


xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(HotSearchWords, HotSearchAdmin)


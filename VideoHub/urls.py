"""videohub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.static import serve

# django rest_framework
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from VideoHub.settings import MEDIA_ROOT, STATICFILES_DIRS

import xadmin

from users.views import SmsCodeViewSet, UserViewSet
from video.views.apiview import VideoListViewSet, CategoryViewSet, HotSearchsViewSet, VideoViewSet

# 通过router绑定url
router = DefaultRouter()
# 配置goods url
router.register(r'videoList', VideoListViewSet, base_name="videos")
router.register(r'video', VideoViewSet, base_name='video')
# 配置category url
router.register(r'categorys', CategoryViewSet, base_name='categorys')
# 验证码
router.register(r'code', SmsCodeViewSet, base_name='code')
# 热门搜索
router.register(r'hotsearchs', HotSearchsViewSet, base_name='hotsearchs')
# 用户
router.register(r'users', UserViewSet, 'users')

video_list = VideoListViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^', include(router.urls)),

    # drf自带的认证方式
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # jwt的认证方式
    url(r'^login/', obtain_jwt_token),
    # drf 文档
    url(r'docs/', include_docs_urls(title="Video hub api docs")),
]

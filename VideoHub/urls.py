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
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

from VideoHub.settings import MEDIA_ROOT, STATIC_ROOT, drf_docs_schema_url

import xadmin

from users.views import SmsCodeViewSet, UserViewSet
from video.views.apiview import VideotViewSet, HotSearchsViewSet
from user_operation.views import UserPublishedListViewSet, UserHomeListViewSet
from pinax.likes.apiviews import LikeToggleView

# 通过router绑定url
router = DefaultRouter()
# 配置videos url
router.register(r'videos', VideotViewSet, base_name="videos")

# 验证码
router.register(r'code', SmsCodeViewSet, base_name='code')
# 热门搜索
router.register(r'hot_searchs', HotSearchsViewSet, base_name='hot_searchs')
# 用户
router.register(r'users', UserViewSet, base_name='users')

# 时光轴
router.register(r'vtimeline', UserPublishedListViewSet, base_name="vtimeline")
router.register(r'user_home', UserHomeListViewSet, base_name='user_home')

# 用户点赞列表、添加点赞、删除点赞 6
# select *from django_content_type
router.register(r'likes', LikeToggleView, base_name='likes')


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^api/', include(router.urls)),

    url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}, name='static'),

    # jwt的认证方式， 在iOS端使用的是jwt的认证方式，未使用rf自带的认证方式
    url(r'^api/login/', obtain_jwt_token),
    # 接受心跳包，验证jwt token是否有效，如果无效则以退出登陆
    url(r'^api/heartbeat/', verify_jwt_token),

    # drf 文档
    url(r'api/docs/', include_docs_urls(title="Video hub api docs", schema_url=drf_docs_schema_url)),
    # url(r"^api/likes/", include("pinax.likes.urls", namespace="pinax_likes")),

    # drf自带的认证方式 web
    # drf登陆的路由为auth/drf/login/ 退出为auth/drf/logout/
    url(r'^auth/drf/', include('rest_framework.urls', namespace='rest_framework')),

    # 测试聊天的页面
    url(r'test/chat/', include('django_private_chat.urls')),
]

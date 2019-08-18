# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import view

urlpatterns = [
    url(
        regex=r'^dialogs/(?P<username>[\w.@+-]+)$',
        view=view.DialogListView.as_view(),
        name='dialogs_detail'
    ),
    url(
        regex=r'^dialogs/$',
        view=view.DialogListView.as_view(),
        name='dialogs'
    ),
    url(
        regex=r'^$',
        view=view.UserListView.as_view(),
        name='user_list'
    ),
]

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django_private_chat import models
from django_private_chat import utils
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth import get_user_model

class UserListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'django_private_chat/users.html'
    login_url = '/xadmin/'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data()
        return context


class DialogListView(LoginRequiredMixin, generic.ListView):
    '''
    与某个用户对话
    url中获取这个username
    '''
    template_name = 'django_private_chat/dialogs.html'
    model = models.Dialog
    ordering = 'modified'

    def get_queryset(self):
        dialogs = models.Dialog.objects.filter(Q(owner=self.request.user) | Q(opponent=self.request.user))
        return dialogs

    def get_context_data(self, **kwargs):
        context = super(DialogListView, self).get_context_data()
        if self.kwargs.get('username'):
            # TODO: show alert that user is not found instead of 404
            user = get_object_or_404(get_user_model(), username=self.kwargs.get('username'))
            dialog = utils.get_dialogs_with_user(self.request.user, user)
            if len(dialog) == 0:
                dialog = models.Dialog.objects.create(owner=self.request.user, opponent=user)
            else:
                dialog = dialog[0]
            context['active_dialog'] = dialog
        else:
            context['active_dialog'] = self.object_list[0]
        if self.request.user == context['active_dialog'].owner:
            context['opponent_username'] = context['active_dialog'].opponent.username
        else:
            context['opponent_username'] = context['active_dialog'].owner.username
        context['ws_server_path'] = '{}://{}:{}/{}'.format(
            settings.CHAT_WS_CLIENT_PROTOCOL,
            settings.CHAT_WS_CLIENT_HOST,
            settings.CHAT_WS_CLIENT_PORT,
            settings.CHAT_WS_CLIENT_ROUTE
        )
        return context

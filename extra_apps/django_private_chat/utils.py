from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from rest_framework_jwt.utils import jwt_decode_handler, jwt_get_username_from_payload_handler

from .models import Dialog
from django.db.models import Q
import logging
import sys

User = get_user_model()

def get_user_from_session(session_key):
    """
    Gets the user from current User model using the passed session_key
    :param session_key: django.contrib.sessions.models.Session - session_key
    :return: User instance or None if not found
    """
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    uid = session_data.get('_auth_user_id')
    user = get_user_model().objects.filter(id=uid).first()  # get object or none
    return user

def get_user_from_jwt_token(token):
    """
    根据jwt_token 获取用户
    :param token: token
    :return: User instance or None if not found
    """
    # 根据token获取jwt 的 payload
    payload = jwt_decode_handler(token=token)
    # 根据payload 获取username
    username = jwt_get_username_from_payload_handler(payload=payload)

    if not username:
       return None

    # Make sure user exists
    try:
        user = User.objects.get_by_natural_key(username)
    except User.DoesNotExist:
        return None

    if not user.is_active:
        return None

    return user

def get_dialogs_with_user(user_1, user_2):
    """
    gets the dialog between user_1 and user_2
    :param user_1: the first user in dialog (owner or opponent)
    :param user_2: the second user in dialog (owner or opponent)
    :return: queryset which include dialog between user_1 and user_2 (queryset can be empty)
    """
    return Dialog.objects.filter(
        Q(owner=user_1, opponent=user_2) | Q(opponent=user_1, owner=user_2))


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    datefmt='%d.%m.%y %H:%M:%S')
logger = logging.getLogger('django-private-dialog')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

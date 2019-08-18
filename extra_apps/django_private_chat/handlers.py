from urllib import parse
import asyncio
import json
import logging
import websockets
from django.contrib.auth import get_user_model
from . import models, router
from .utils import get_dialogs_with_user, get_user_from_session, get_user_from_jwt_token

logger = logging.getLogger('django-private-dialog')
ws_connections = {}


# ws_auth_type 为客户端连接websocket服务端的鉴权字段，有两种方式：session_key 和 jwt_token
ws_auth_type_jwt_token = "token"
ws_auth_type_session_key = "session_key"
ws_auth_type_list = [ws_auth_type_jwt_token, ws_auth_type_session_key]

def get_user_from_auth_id(auth_key, auth_type):
    if auth_type == ws_auth_type_session_key:
        return get_user_from_session(auth_key)
    return get_user_from_jwt_token(auth_key)

def get_auth_from_packet(packet_dict={}):
    '''
    同时支持token 和 session 的请求方式
    :param packet_dict:
    :return: auth_id, auth_type
    '''
    if not packet_dict or not isinstance(packet_dict, dict) or not len(packet_dict):
        return
    auth_type = None
    auth_id = None
    for _auth_type in ws_auth_type_list:
        _auth_id = packet_dict.get(_auth_type)
        if _auth_id and len(_auth_id) > 0:
            # 匹配ws url参数中的ws_auth_type，找到了就全局使用此授权方式
            # 根据客户端连接请求的参数，确定使用哪一种授权方式
            auth_type = _auth_type
            auth_id = _auth_id
            break
    if auth_type is None or auth_id is None:
        err = "Don't Got None (auth_type or auth_id) attempt to connect "
        logger.info(err)
        return
    return auth_id, auth_type

def ws_authenticate(websocet, path):

    # 对 连接websocket的url的参数进行解析

    # url解码
    url_data = parse.unquote(path)
    # url结果
    url_result = parse.urlparse(url_data)
    # 解析url里面的参数
    query_dict = parse.parse_qs(url_result.query)

    opponent_username = query_dict.get('opponent', "")[0]

    auth_id = None
    auth_type = None
    for _auth_type in ws_auth_type_list:
        auth_key = query_dict.get(_auth_type, [])
        if len(auth_key) > 0:
            # 匹配ws url参数中的ws_auth_type，找到了就全局使用此授权方式
            # 根据客户端连接请求的参数，确定使用哪一种授权方式
            auth_type = _auth_type
            auth_id = auth_key[0]
            break
    if auth_type is None or auth_id is None:
        err = "Don't Got None (auth_type or auth_id) attempt to connect "
        logger.info(err)
        return

    return get_user_from_auth_id(auth_id, auth_type), opponent_username

@asyncio.coroutine
def target_message(conn, payload):
    """
    Distibuted payload (message) to one connection
    :param conn: connection
    :param payload: payload(json dumpable)
    :return:
    """
    try:
        yield from conn.send(json.dumps(payload))
    except Exception as e:
        logger.debug('could not send', e)


@asyncio.coroutine
def fanout_message(connections, payload):
    """
    Distributes payload (message) to all connected ws clients
    """
    for conn in connections:
        try:
            yield from conn.send(json.dumps(payload))
        except Exception as e:
            logger.debug('could not send', e)


@asyncio.coroutine
def gone_online(stream):
    """
    Distributes the users online status to everyone he has dialog with
    """
    while True:
        packet = yield from stream.get()
        auth_id, auth_type = get_auth_from_packet(packet)
        if auth_id:
            user_owner = get_user_from_auth_id(auth_id, auth_type)
            if user_owner:
                logger.debug('User ' + user_owner.username + ' gone online')
                # find all connections including user_owner as opponent,
                # send them a message that the user has gone online
                online_opponents = list(filter(lambda x: x[1] == user_owner.username, ws_connections))
                online_opponents_sockets = [ws_connections[i] for i in online_opponents]
                yield from fanout_message(online_opponents_sockets,
                                          {'type': 'gone-online', 'usernames': [user_owner.username]})
            else:
                pass  # invalid session id
        else:
            pass  # no session id


@asyncio.coroutine
def check_online(stream):
    """
    Used to check user's online opponents and show their online/offline status on page on init
    """
    while True:
        packet = yield from stream.get()
        auth_id, auth_type = get_auth_from_packet(packet)
        opponent_username = packet.get('username')
        if auth_id and opponent_username:
            user_owner = get_user_from_auth_id(auth_id, auth_type)
            if user_owner:
                # Find all connections including user_owner as opponent
                online_opponents = list(filter(lambda x: x[1] == user_owner.username, ws_connections))
                logger.debug('User ' + user_owner.username + ' has ' + str(len(online_opponents)) + ' opponents online')
                # Send user online statuses of his opponents
                socket = ws_connections.get((user_owner.username, opponent_username))
                if socket:
                    online_opponents_usernames = [i[0] for i in online_opponents]
                    yield from target_message(socket,
                                              {'type': 'gone-online', 'usernames': online_opponents_usernames})
                else:
                    pass  # socket for the pair user_owner.username, opponent_username not found
                    # this can be in case the user has already gone offline
            else:
                pass  # invalid session id
        else:
            pass  # no session id or opponent username


@asyncio.coroutine
def gone_offline(stream):
    """
    Distributes the users online status to everyone he has dialog with
    """
    while True:
        packet = yield from stream.get()
        auth_id, auth_type = get_auth_from_packet(packet)
        if auth_id:
            user_owner = get_user_from_auth_id(auth_id, auth_type)
            if user_owner:
                logger.debug('User ' + user_owner.username + ' gone offline')
                # find all connections including user_owner as opponent,
                #  send them a message that the user has gone offline
                online_opponents = list(filter(lambda x: x[1] == user_owner.username, ws_connections))
                online_opponents_sockets = [ws_connections[i] for i in online_opponents]
                yield from fanout_message(online_opponents_sockets,
                                          {'type': 'gone-offline', 'username': user_owner.username})
            else:
                pass  # invalid session id
        else:
            pass  # no session id


@asyncio.coroutine
def new_messages_handler(stream):
    """
    将新的聊天信息保存到数据库并将消息分发给已连接的用户
    Saves a new chat message to db and distributes msg to connected users
    """
    # TODO: handle no user found exception
    while True:
        packet = yield from stream.get()
        auth_id, auth_type = get_auth_from_packet(packet)
        msg = packet.get('message')
        username_opponent = packet.get('username')
        if auth_id and msg and username_opponent:
            user_owner = get_user_from_auth_id(auth_id, auth_type)
            if user_owner:
                user_opponent = get_user_model().objects.get(username=username_opponent)
                dialog = get_dialogs_with_user(user_owner, user_opponent)
                if len(dialog) > 0:
                    # Save the message
                    msg = models.Message.objects.create(
                        dialog=dialog[0],
                        sender=user_owner,
                        text=packet['message'],
                        read=False
                    )
                    packet['created'] = msg.get_formatted_create_datetime()
                    packet['sender_name'] = msg.sender.username
                    packet['message_id'] = msg.id
                    # 移除消息中auth
                    [packet.pop(key) for key in ws_auth_type_list if key in packet.keys()]

                    # Send the message
                    connections = []
                    # Find socket of the user which sent the message
                    if (user_owner.username, user_opponent.username) in ws_connections:
                        connections.append(ws_connections[(user_owner.username, user_opponent.username)])
                    # Find socket of the opponent
                    if (user_opponent.username, user_owner.username) in ws_connections:
                        connections.append(ws_connections[(user_opponent.username, user_owner.username)])
                    else:
                        # Find sockets of people who the opponent is talking with
                        opponent_connections = list(filter(lambda x: x[0] == user_opponent.username, ws_connections))
                        opponent_connections_sockets = [ws_connections[i] for i in opponent_connections]
                        connections.extend(opponent_connections_sockets)

                    yield from fanout_message(connections, packet)
                else:
                    pass  # no dialog found
            else:
                pass  # no user_owner
        else:
            pass  # missing one of params


@asyncio.coroutine
def users_changed_handler(stream):
    """
    发送聊天室中当前活动用户的已连接客户端列表
    Sends connected client list of currently active users in the chatroom
    """
    while True:
        yield from stream.get()

        # Get list list of current active users
        users = [
            {'username': username, 'uuid': uuid_str}
            for username, uuid_str in ws_connections.values()
        ]

        # Make packet with list of new users (sorted by username)
        packet = {
            'type': 'users-changed',
            'value': sorted(users, key=lambda i: i['username'])
        }
        logger.debug(packet)
        yield from fanout_message(ws_connections.keys(), packet)


@asyncio.coroutine
def is_typing_handler(stream):
    """
    Show message to opponent if user is typing message
    """
    while True:
        packet = yield from stream.get()
        auth_id, auth_type = get_auth_from_packet(packet)
        user_opponent = packet.get('username')
        typing = packet.get('typing')
        if auth_id and user_opponent and typing is not None:
            user_owner = get_user_from_auth_id(auth_id, auth_type)
            if user_owner:
                opponent_socket = ws_connections.get((user_opponent, user_owner.username))
                if typing and opponent_socket:
                    yield from target_message(opponent_socket,
                                              {'type': 'opponent-typing', 'username': user_opponent})
            else:
                pass  # invalid session id
        else:
            pass  # no session id or user_opponent or typing


@asyncio.coroutine
def read_message_handler(stream):
    """
    如果对方已阅读消息，则向用户发送消息
    Send message to user if the opponent has read the message
    """
    while True:
        packet = yield from stream.get()
        auth_id, auth_type = get_auth_from_packet(packet)
        user_opponent = packet.get('username')
        message_id = packet.get('message_id')
        if auth_id and user_opponent and message_id is not None:
            user_owner = get_user_from_auth_id(auth_id, auth_type)
            if user_owner:
                message = models.Message.objects.filter(id=message_id).first()
                if message:
                    message.read = True
                    message.save()
                    logger.debug('Message ' + str(message_id) + ' is now read')
                    opponent_socket = ws_connections.get((user_opponent, user_owner.username))
                    if opponent_socket:
                        yield from target_message(opponent_socket,
                                                  {'type': 'opponent-read-message',
                                                   'username': user_opponent, 'message_id': message_id})
                else:
                    pass  # message not found
            else:
                pass  # invalid session id
        else:
            pass  # no session id or user_opponent or typing


@asyncio.coroutine
def main_handler(websocket, path):
    """
    创建一个websocket连接的回调处理
    An Asyncio Task is created for every new websocket client connection
    that is established. This coroutine listens to messages from the connected
    client and routes the message to the proper queue.

    This coroutine can be thought of as a producer.
    path: ws://127.0.0.1:5002/?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjE4OTAxMTA4NzE5IiwiZXhwIjoxNTY2Mjc2OTc2LCJlbWFpbCI6IiIsIm1vYmlsZSI6IjE4OTAxMTA4NzE5In0.IzgSstfFrDB2ehf778HHx-2Hrw6YDE54_sexFAhC9Z0&opponent=xiaoyuan
    """
    user_owner, opponent_username = ws_authenticate(websocket, path)
    if user_owner:
        user_owner = user_owner.username
        # Persist users connection, associate user w/a unique ID
        ws_connections[(user_owner, opponent_username)] = websocket

        # While the websocket is open, listen for incoming messages/events
        # if unable to listening for messages/events, then disconnect the client
        try:
            while websocket.open:
                data = yield from websocket.recv()
                if not data:
                    continue
                logger.debug(data)
                try:
                    yield from router.MessageRouter(data)()
                except Exception as e:
                    logger.error('could not route msg', e)

        except websockets.exceptions.InvalidState:  # User disconnected
            pass
        finally:
            del ws_connections[(user_owner, opponent_username)]
    else:
        logger.info("Not user owner,  Got invalid auth_id attempt to connect ")

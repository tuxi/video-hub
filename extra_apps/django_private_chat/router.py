import asyncio
import json
import logging

from .channels import new_messages, users_changed, online, offline, check_online, is_typing, read_unread

logger = logging.getLogger('django-private-dialog')


class MessageRouter(object):
    # 接收客户端发送的不同消息类型队列
    MESSAGE_QUEUES = {
        'new-message': new_messages,
        'new-user': users_changed,
        'online': online,
        'offline': offline,
        'check-online': check_online,
        'is-typing': is_typing,
        'read_message': read_unread
    }

    def __init__(self, data):
        try:
            self.packet = json.loads(data)
        except Exception as e:
            logger.debug('could not load json: {}'.format(str(e)))

    def get_packet_type(self):
        return self.packet['type']

    @asyncio.coroutine
    def __call__(self):
        logger.debug('routing message: {}'.format(self.packet))
        send_queue = self.get_send_queue()
        yield from send_queue.put(self.packet)

    def get_send_queue(self):
        '''
        根据type获取当前要发送的消息队列
        :return: 当前消息队列
        '''
        return self.MESSAGE_QUEUES[self.get_packet_type()]

# -*- coding: utf-8 -*-
"""
apps.notifications.consumers - WebSocket 消费者

提供实验实时推送和用户通知推送的 WebSocket 消费者。
使用 Django Channels 实现，替换 Java Pushlet。

WebSocket 路由在 routing.py 中注册：
- ws/experiment/<experiment_id>/ → ExperimentConsumer
- ws/notifications/<user_id>/    → NotificationConsumer
"""

import json
import logging
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.notifications.serializers import WebSocketMessageSerializer

logger = logging.getLogger(__name__)


# ============================================================================
# 实验实时推送 Consumer
# ============================================================================

class ExperimentConsumer(AsyncWebsocketConsumer):
    """实验实时推送 WebSocket 消费者

    连接：ws://host/ws/experiment/<experiment_id>/
    功能：接收实验操作数据并广播给同实验的所有用户
    用途：替换 Java 的 Pushlet，实现实验协作的实时数据同步

    组名格式：experiment_{experiment_id}

    从客户端接收的消息格式：
    {
        "type": "experiment_action",
        "data": { ... },  // 实验操作数据
        "timestamp": 1717488000000
    }

    广播给同组成员的格式：
    {
        "type": "experiment_action",
        "data": { ... },
        "timestamp": 1717488000000,
        "userId": 123
    }
    """

    async def connect(self):
        """建立 WebSocket 连接

        从 URL 中提取 experiment_id，并将其加入对应的 Channel Layer 组。
        """
        self.experiment_id = self.scope['url_route']['kwargs']['experiment_id']
        self.group_name = f'experiment_{self.experiment_id}'

        # 加入实验组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()
        logger.info(f'ExperimentConsumer 连接建立: experiment_id={self.experiment_id}')

    async def disconnect(self, close_code):
        """断开 WebSocket 连接

        从实验组中移除当前连接。
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        logger.info(
            f'ExperimentConsumer 连接断开: '
            f'experiment_id={self.experiment_id}, close_code={close_code}',
        )

    async def receive(self, text_data=None, bytes_data=None):
        """接收 WebSocket 消息

        将接收到的实验操作数据广播给同实验的所有用户。

        Args:
            text_data: JSON 格式的文本消息（优先）
            bytes_data: 二进制消息（当前不支持）
        """
        try:
            if text_data:
                data = json.loads(text_data)
            else:
                logger.warning('ExperimentConsumer 收到非文本消息，忽略')
                return

            # 获取用户ID（可能未认证）
            user_id = None
            if self.scope['user'].is_authenticated:
                user_id = self.scope['user'].id

            # 验证消息格式（仅做基本校验，不阻止转发）
            data.setdefault('timestamp', datetime.now().timestamp() * 1000)
            data.setdefault('type', 'experiment_action')
            data.setdefault('data', {})

            # 检查是否验证通过的消息格式
            serializer = WebSocketMessageSerializer(data=data)
            serializer.is_valid(raise_exception=False)

            message = serializer.validated_data if serializer.is_valid() else data
            message['userId'] = user_id

            # 广播给同实验的所有用户
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'experiment_broadcast',
                    'message': message,
                },
            )

            logger.debug(
                f'ExperimentConsumer 广播消息: '
                f'experiment_id={self.experiment_id}, type={message.get("type")}',
            )

        except json.JSONDecodeError as e:
            logger.error(f'ExperimentConsumer JSON 解析失败: {e}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'data': {'message': '消息格式错误，请发送有效的 JSON'},
            }))
        except Exception as e:
            logger.error(f'ExperimentConsumer 处理消息异常: {e}', exc_info=True)

    async def experiment_broadcast(self, event):
        """广播实验数据到当前连接

        由 channel_layer.group_send 触发。
        event 中的 message 对象会通过 WebSocket 推送到客户端。

        Args:
            event: {
                'type': 'experiment_broadcast',
                'message': { ... }
            }
        """
        message = event['message']

        # 发送给当前 WebSocket 客户端
        await self.send(text_data=json.dumps(message, ensure_ascii=False))


# ============================================================================
# 用户通知 Consumer
# ============================================================================

class NotificationConsumer(AsyncWebsocketConsumer):
    """用户通知 WebSocket 消费者

    连接：ws://host/ws/notifications/<user_id>/
    功能：向指定用户推送通知（系统通知、实验评分通知等）

    组名格式：notifications_{user_id}

    推送通知格式：
    {
        "type": "notification",
        "data": {
            "id": 1,
            "type": "experiment_grade",
            "title": "实验评分通知",
            "content": "您的实验「xxx」已评分",
            "userId": 123,
            "isRead": false,
            "createTime": "2024-06-04T10:00:00Z"
        },
        "timestamp": 1717488000000
    }
    """

    async def connect(self):
        """建立 WebSocket 连接

        从 URL 中提取 user_id，并将其加入对应的通知组。
        """
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'

        # 加入用户通知组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()
        logger.info(f'NotificationConsumer 连接建立: user_id={self.user_id}')

    async def disconnect(self, close_code):
        """断开 WebSocket 连接

        从用户通知组中移除当前连接。
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        logger.info(
            f'NotificationConsumer 连接断开: '
            f'user_id={self.user_id}, close_code={close_code}',
        )

    async def receive(self, text_data=None, bytes_data=None):
        """接收 WebSocket 消息

        通知 Consumer 通常只收不发，客户端发送的消息记录到日志。

        Args:
            text_data: JSON 格式的文本消息
            bytes_data: 二进制消息
        """
        try:
            if text_data:
                data = json.loads(text_data)

                # 通知通道通常只用于接收推送，客户端发送的消息主要是 ping/pong
                msg_type = data.get('type', 'unknown')
                if msg_type == 'ping':
                    await self.send(text_data=json.dumps({
                        'type': 'pong',
                        'data': {},
                        'timestamp': datetime.now().timestamp() * 1000,
                    }))
                else:
                    logger.debug(
                        f'NotificationConsumer 收到客户端消息: '
                        f'user_id={self.user_id}, type={msg_type}',
                    )

        except json.JSONDecodeError as e:
            logger.error(f'NotificationConsumer JSON 解析失败: {e}')
        except Exception as e:
            logger.error(f'NotificationConsumer 处理消息异常: {e}', exc_info=True)

    async def send_notification(self, event):
        """推送通知到当前连接

        由外部服务通过 channel_layer.group_send 调用。
        调用示例：
            await channel_layer.group_send(
                'notifications_{user_id}',
                {
                    'type': 'send_notification',
                    'message': notification_data,
                },
            )

        Args:
            event: {
                'type': 'send_notification',
                'message': { ... }
            }
        """
        message = event['message']

        await self.send(text_data=json.dumps(message, ensure_ascii=False))
        logger.debug(f'NotificationConsumer 推送通知: user_id={self.user_id}')

# -*- coding: utf-8 -*-
"""
apps.notifications.serializers - 消息通知 序列化器

提供通知消息、短信发送、WebSocket 消息等序列化器。
注意：该 App 没有独立数据库表，所有序列化器均为非 Model 绑定。
"""

from rest_framework import serializers


# ============================================================================
# 通知消息
# ============================================================================

class NotificationSerializer(serializers.Serializer):
    """通知消息序列化器

    用于 WebSocket 推送通知的序列化与反序列化。
    字段：id, type, title, content, userId, isRead, createTime
    """

    id = serializers.IntegerField(read_only=True, help_text='通知ID')
    type = serializers.CharField(max_length=50, help_text='通知类型（如 experiment_grade, system, course_update 等）')
    title = serializers.CharField(max_length=255, help_text='通知标题')
    content = serializers.CharField(help_text='通知内容')
    userId = serializers.IntegerField(help_text='接收用户ID')
    isRead = serializers.BooleanField(default=False, help_text='是否已读')
    createTime = serializers.DateTimeField(read_only=True, help_text='创建时间')


# ============================================================================
# 短信发送
# ============================================================================

class SmsSerializer(serializers.Serializer):
    """短信发送序列化器

    用于发送短信验证码等通知。
    输入字段：telephone（手机号）, template（短信模板标识）

    注意：
      - 开发环境：仅打印验证码日志，不真实发送
      - 生产环境：接入阿里云短信 SDK
    """

    telephone = serializers.CharField(
        max_length=20,
        help_text='接收短信的手机号码',
    )
    template = serializers.ChoiceField(
        choices=['captcha', 'notice', 'alert'],
        help_text='短信模板标识：captcha（验证码）, notice（通知）, alert（告警）',
    )


# ============================================================================
# WebSocket 消息
# ============================================================================

class WebSocketMessageSerializer(serializers.Serializer):
    """WebSocket 消息序列化器

    用于 WebSocket 通道中传输消息的通用格式。
    字段：type（消息类型）, data（消息内容）, timestamp（时间戳）
    """

    type = serializers.CharField(max_length=50, help_text='消息类型（如 experiment_status, notification, ping 等）')
    data = serializers.JSONField(help_text='消息内容，JSON 格式')
    timestamp = serializers.FloatField(help_text='消息时间戳（Unix 毫秒时间戳）')

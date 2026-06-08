# -*- coding: utf-8 -*-
"""
utils.sms - 短信服务工具

统一短信发送接口，后续接入具体服务商（阿里云/腾讯云）。
"""

import logging

logger = logging.getLogger(__name__)


class SMSClient:
    """
    短信客户端基类 - 后续子类实现具体服务商

    使用:
      client = SMSClient()
      client.send_verification_code('13800138000', '123456')
    """

    def send(self, phone: str, content: str, template_id: str = None,
             template_params: dict = None) -> bool:
        """
        发送短信

        Args:
            phone:           手机号
            content:         短信内容（直接发送模式）
            template_id:     模板 ID（模板模式）
            template_params: 模板参数

        Returns:
            bool: 是否发送成功
        """
        raise NotImplementedError('子类需实现 send 方法')

    def send_verification_code(self, phone: str, code: str) -> bool:
        """
        发送验证码

        Args:
            phone: 手机号
            code:  验证码

        Returns:
            bool: 是否发送成功
        """
        raise NotImplementedError('子类需实现 send_verification_code 方法')


class ConsoleSMSClient(SMSClient):
    """
    开发环境控制台短信客户端（仅打印日志）
    """

    def send(self, phone: str, content: str, template_id: str = None,
             template_params: dict = None) -> bool:
        logger.info(f'[SMS/Console] 发送到 {phone}: {content}')
        return True

    def send_verification_code(self, phone: str, code: str) -> bool:
        logger.info(f'[SMS/Console] 验证码发送到 {phone}: {code}')
        return True


# 默认客户端（开发环境）
sms_client: SMSClient = ConsoleSMSClient()

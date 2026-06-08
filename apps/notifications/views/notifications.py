# -*- coding: utf-8 -*-
"""
apps.notifications.views.notifications - 消息通知 视图

提供短信发送、通知管理等接口。
"""

import logging
import random

from django.conf import settings

from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.serializers import SmsSerializer

logger = logging.getLogger(__name__)


# ============================================================================
# 发送短信
# ============================================================================

class SendSmsView(APIView):
    """发送短信（短信验证码）

    POST /api/v1/notifications/send-sms/
    匿名可访问

    发送短信验证码到指定手机号。
    - 开发环境：console 输出验证码（6位随机数），不真实发送
    - 生产环境：接入阿里云短信 SDK

    请求体:
    {
        "telephone": "13800138000",
        "template": "captcha"   // captcha | notice | alert
    }

    响应:
    {
        "message": "验证码已发送",
        "code": "sent"
    }
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # 匿名访问

    def post(self, request):
        serializer = SmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telephone = serializer.validated_data['telephone']
        template = serializer.validated_data['template']

        # 生成 6 位随机验证码
        captcha_code = ''.join(random.choices('0123456789', k=6))

        if settings.DEBUG:
            # 开发环境：控制台输出验证码
            logger.info('=' * 60)
            logger.info(f'【短信验证码 - 开发环境】')
            logger.info(f'    手机号: {telephone}')
            logger.info(f'    模板:   {template}')
            logger.info(f'    验证码: {captcha_code}')
            logger.info(f'    提示:   开发环境仅打印日志，未真实发送短信')
            logger.info('=' * 60)
        else:
            # 生产环境：接入阿里云短信 SDK
            self._send_real_sms(telephone, template, captcha_code)

        return Response(
            {'message': '验证码已发送', 'code': 'sent'},
            status=status.HTTP_200_OK,
        )

    def _send_real_sms(self, telephone: str, template: str, code: str) -> None:
        """真实发送短信（生产环境）

        接入阿里云短信 SDK（aliyunsdkdysmsapi）。
        需要配置环境变量：
          - ALIYUN_SMS_ACCESS_KEY_ID
          - ALIYUN_SMS_ACCESS_KEY_SECRET
          - ALIYUN_SMS_SIGN_NAME（短信签名）

        Args:
            telephone: 接收手机号
            template: 短信模板标识
            code: 验证码

        Raises:
            Exception: 发送失败时抛出
        """
        # TODO: 生产环境接入阿里云短信 SDK
        # from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
        # from aliyunsdkcore.client import AcsClient
        #
        # client = AcsClient(
        #     settings.ALIYUN_SMS_ACCESS_KEY_ID,
        #     settings.ALIYUN_SMS_ACCESS_KEY_SECRET,
        #     'cn-hangzhou',
        # )
        #
        # template_codes = {
        #     'captcha': 'SMS_XXXXX',  # 验证码模板
        #     'notice': 'SMS_XXXXX',   # 通知模板
        #     'alert': 'SMS_XXXXX',    # 告警模板
        # }
        #
        # request = SendSmsRequest.SendSmsRequest()
        # request.set_TelphoneNumbers(telephone)
        # request.set_SignName(settings.ALIYUN_SMS_SIGN_NAME)
        # request.set_TemplateCode(template_codes.get(template, template_codes['captcha']))
        # request.set_TemplateParam(json.dumps({'code': code}))
        #
        # response = client.do_action_with_exception(request)
        # logger.info(f'短信发送结果: {response}')

        logger.warning(
            '生产环境短信发送暂未实现，请接入阿里云短信 SDK。'
            f'telephone={telephone}, template={template}, code={code}',
        )

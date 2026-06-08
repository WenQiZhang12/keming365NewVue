# -*- coding: utf-8 -*-
"""
utils.exceptions - 统一异常处理

所有 API 异常返回统一格式：
  {
    "code":    错误码（字符串，便于前端判断），
    "message": 人类可读的错误描述，
    "details": 详细错误信息（可选，表单校验等场景）
  }
"""

import logging
import traceback

from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import set_rollback

logger = logging.getLogger(__name__)


# ============================================================================
# 自定义异常基类
# ============================================================================


class BusinessError(APIException):
    """
    业务异常基类

    使用示例:
      raise BusinessError(
          message='用户不存在',
          code='USER_NOT_FOUND',
          status_code=404,
      )
    """

    def __init__(self, message='业务异常', code='BUSINESS_ERROR', status_code=400, details=None):
        self.status_code = status_code
        self.code = code
        self.detail = {
            'code': code,
            'message': message,
            'details': details or {},
        }


class ServiceUnavailableError(BusinessError):
    """服务不可用"""

    def __init__(self, message='服务暂时不可用，请稍后重试', details=None):
        super().__init__(
            message=message,
            code='SERVICE_UNAVAILABLE',
            status_code=503,
            details=details,
        )


# ============================================================================
# 异常映射表
# ============================================================================

_exception_handlers = {}


def register_exception_handler(exc_class):
    """
    注册异常处理器装饰器

    使用示例:
      @register_exception_handler(MyCustomError)
      def handle_my_error(exc, context):
          return Response({'code': 'XX', 'message': str(exc)}, status=400)
    """

    def decorator(handler_func):
        _exception_handlers[exc_class] = handler_func
        return handler_func

    return decorator


# ============================================================================
# 统一异常处理入口
# ============================================================================


def custom_exception_handler(exc, context):
    """
    DRF 统一异常处理器

    返回格式:
      {
        "code": "ERROR_CODE",
        "message": "人类可读描述",
        "details": {}
      }
    """

    # 先检查是否有自定义处理器
    if isinstance(exc, APIException):
        for exc_class in type(exc).__mro__:
            if exc_class in _exception_handlers:
                return _exception_handlers[exc_class](exc, context)

    # --- 已知 DRF/HTTP 异常处理 ---

    if isinstance(exc, ValidationError):
        set_rollback()
        return Response(
            {
                'code': 'VALIDATION_ERROR',
                'message': '数据校验失败',
                'details': exc.detail,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, AuthenticationFailed):
        set_rollback()
        return Response(
            {
                'code': 'AUTH_FAILED',
                'message': '认证失败：' + str(exc.detail),
                'details': {},
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, NotAuthenticated):
        set_rollback()
        return Response(
            {
                'code': 'NOT_AUTHENTICATED',
                'message': '请先登录',
                'details': {},
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, PermissionDenied):
        set_rollback()
        return Response(
            {
                'code': 'PERMISSION_DENIED',
                'message': '没有权限执行此操作',
                'details': {},
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, (NotFound, Http404)):
        set_rollback()
        return Response(
            {
                'code': 'NOT_FOUND',
                'message': '请求的资源不存在',
                'details': {},
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, MethodNotAllowed):
        set_rollback()
        return Response(
            {
                'code': 'METHOD_NOT_ALLOWED',
                'message': '不支持的请求方法',
                'details': {},
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    if isinstance(exc, ParseError):
        set_rollback()
        return Response(
            {
                'code': 'PARSE_ERROR',
                'message': '请求格式错误',
                'details': {},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, Throttled):
        return Response(
            {
                'code': 'THROTTLED',
                'message': f'请求过于频繁，请 {exc.wait} 秒后重试',
                'details': {},
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if isinstance(exc, BusinessError):
        set_rollback()
        return Response(
            exc.detail,
            status=exc.status_code,
        )

    if isinstance(exc, APIException):
        set_rollback()
        return Response(
            {
                'code': 'API_ERROR',
                'message': str(exc.detail) if exc.detail else '服务器错误',
                'details': {},
            },
            status=exc.status_code,
        )

    # --- 未知异常：500 ---
    logger.exception('Unhandled exception: %s', exc)
    set_rollback()
    return Response(
        {
            'code': 'INTERNAL_ERROR',
            'message': '服务器内部错误，请稍后重试',
            'details': {},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

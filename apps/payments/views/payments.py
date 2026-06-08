# -*- coding: utf-8 -*-
"""
apps.payments.views.payments - 支付与订单 视图

提供商品列表、订单创建/列表、支付等接口。
"""

import logging

from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import Orders, Product
from apps.payments.serializers import (
    AlipayPaySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    ProductSerializer,
    WxpayPaySerializer,
)
from utils.exceptions import BusinessError
from utils.pagination import StandardPagination

logger = logging.getLogger(__name__)


# ============================================================================
# 商品列表
# ============================================================================

class ProductListView(APIView, StandardPagination):
    """商品列表

    GET /api/v1/payments/products/
    匿名可访问

    返回所有上架商品列表，支持分页。

    查询参数:
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
    """

    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Product.objects.all().order_by('id')

        page = self.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# 创建订单
# ============================================================================

class OrderCreateView(APIView):
    """创建订单

    POST /api/v1/payments/orders/create/
    需要登录

    请求体:
      {
        "productId": "商品 ID",
        "paymentType": 1   // 1=支付宝, 2=微信
      }

    返回:
      {
        "id": 订单ID,
        "orderNum": "订单号",
        "totalFee": "金额",
        "status": "0",
        "createTime": "创建时间"
      }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        return Response({
            'id': order.id,
            'orderNum': order.orderNum,
            'totalFee': order.orderAmount,
            'status': order.orderStatus,
            'createTime': order.createTime,
        }, status=status.HTTP_201_CREATED)


# ============================================================================
# 我的订单列表
# ============================================================================

class OrderListView(APIView, StandardPagination):
    """我的订单列表

    GET /api/v1/payments/orders/
    需要登录

    返回当前登录用户的订单列表，按创建时间倒序排列，支持分页。

    查询参数:
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        queryset = Orders.objects.filter(
            userId=str(user_id),
        ).order_by('-createTime')

        page = self.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# 支付宝支付
# ============================================================================

class AlipayPayView(APIView):
    """支付宝支付

    POST /api/v1/payments/orders/<id>/pay/alipay/
    需要登录

    简化实现：返回模拟支付宝支付链接，后续替换真实 SDK。

    返回:
      {
        "pay_url": "模拟支付宝支付链接"
      }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = AlipayPaySerializer(
            data={'orderId': order_id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        # 简化实现：返回模拟支付链接
        return Response({
            'pay_url': f'https://pay.alipay.com/mock?order_id={order_id}',
        }, status=status.HTTP_200_OK)


# ============================================================================
# 微信支付
# ============================================================================

class WxpayPayView(APIView):
    """微信支付

    POST /api/v1/payments/orders/<id>/pay/wxpay/
    需要登录

    简化实现：返回模拟微信支付参数，后续替换真实 SDK。

    返回:
      {
        "pay_params": {}
      }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = WxpayPaySerializer(
            data={'orderId': order_id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        # 简化实现：返回模拟支付参数
        return Response({
            'pay_params': {
                'appId': 'mock_app_id',
                'timeStamp': str(int(timezone.now().timestamp())),
                'nonceStr': 'mock_nonce_str',
                'package': 'prepay_id=mock_prepay_id',
                'signType': 'MD5',
                'paySign': 'mock_pay_sign',
            },
        }, status=status.HTTP_200_OK)


# ============================================================================
# 支付宝异步通知回调
# ============================================================================

class AlipayNotifyView(APIView):
    """支付宝异步通知回调

    POST /api/v1/payments/notify/alipay/
    匿名可访问（异步回调）

    简化实现：接收通知并更新订单状态为已支付。
    后续替换真实验签逻辑。
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # 无需认证

    def post(self, request):
        # 简化实现：假设验签通过，更新订单状态
        order_id = request.data.get('order_id') or request.data.get('out_trade_no')
        trade_status = request.data.get('trade_status', 'TRADE_SUCCESS')

        if not order_id:
            logger.warning('支付宝通知缺少订单ID')
            return Response({'code': 'FAIL', 'message': '缺少订单ID'}, status=400)

        if trade_status == 'TRADE_SUCCESS':
            try:
                order = Orders.objects.get(id=order_id)
                order.orderStatus = '1'  # 1=已支付
                order.paidTime = timezone.now()
                order.save(update_fields=['orderStatus', 'paidTime'])
                logger.info(f'支付宝回调：订单 {order_id} 支付成功')
            except Orders.DoesNotExist:
                logger.warning(f'支付宝回调：订单 {order_id} 不存在')
                return Response({'code': 'FAIL', 'message': '订单不存在'}, status=404)

        # 支付宝要求返回 success
        return Response({'code': 'SUCCESS', 'message': 'success'})


# ============================================================================
# 微信异步通知回调
# ============================================================================

class WxpayNotifyView(APIView):
    """微信异步通知回调

    POST /api/v1/payments/notify/wxpay/
    匿名可访问（异步回调）

    简化实现：接收通知并更新订单状态为已支付。
    后续替换真实验签逻辑。
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # 无需认证

    def post(self, request):
        # 简化实现：假设验签通过，更新订单状态
        order_id = request.data.get('order_id') or request.data.get('out_trade_no')
        return_code = request.data.get('return_code', 'SUCCESS')

        if not order_id:
            logger.warning('微信通知缺少订单ID')
            return Response({'code': 'FAIL', 'message': '缺少订单ID'}, status=400)

        if return_code == 'SUCCESS':
            try:
                order = Orders.objects.get(id=order_id)
                order.orderStatus = '1'  # 1=已支付
                order.paidTime = timezone.now()
                order.save(update_fields=['orderStatus', 'paidTime'])
                logger.info(f'微信回调：订单 {order_id} 支付成功')
            except Orders.DoesNotExist:
                logger.warning(f'微信回调：订单 {order_id} 不存在')
                return Response({'code': 'FAIL', 'message': '订单不存在'}, status=404)

        # 微信要求返回 XML 格式的成功标识，此处简化返回 JSON
        return Response({'code': 'SUCCESS', 'message': 'OK'})

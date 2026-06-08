# -*- coding: utf-8 -*-
"""
apps.payments.urls - 支付与订单 路由

路由前缀（在 config/urls.py 中定义）：/api/v1/payments/
"""

from django.urls import path

from apps.payments.views.payments import (
    AlipayNotifyView,
    AlipayPayView,
    OrderCreateView,
    OrderListView,
    ProductListView,
    WxpayNotifyView,
    WxpayPayView,
)

app_name = 'payments'

urlpatterns = [
    # --- 商品 ---
    path('products/', ProductListView.as_view(), name='product_list'),

    # --- 订单 ---
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<str:order_id>/pay/alipay/', AlipayPayView.as_view(), name='alipay_pay'),
    path('orders/<str:order_id>/pay/wxpay/', WxpayPayView.as_view(), name='wxpay_pay'),

    # --- 支付回调 ---
    path('notify/alipay/', AlipayNotifyView.as_view(), name='alipay_notify'),
    path('notify/wxpay/', WxpayNotifyView.as_view(), name='wxpay_notify'),
]

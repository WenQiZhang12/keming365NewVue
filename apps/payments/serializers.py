# -*- coding: utf-8 -*-
"""
apps.payments.serializers - 支付与订单 序列化器

提供商品、订单、支付等序列化器。
"""

import uuid
import logging

from django.utils import timezone

from rest_framework import serializers

from apps.payments.models import Orders, Product

logger = logging.getLogger(__name__)


# ============================================================================
# 商品序列化器
# ============================================================================

class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器

    字段：id, name, price, description, image, createTime
    """

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'description',
            'image',
            'createTime',
        ]


# ============================================================================
# 订单序列化器
# ============================================================================

class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器

    字段：id, orderNum, userId, productId, productName, totalFee, paymentType, status, createTime, payTime
    """

    productName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Orders
        fields = [
            'id',
            'orderNum',
            'userId',
            'productId',
            'productName',
            'totalFee',
            'paymentType',
            'status',
            'createTime',
            'payTime',
        ]

    def get_productName(self, obj) -> str:
        """获取商品名称"""
        if obj.productId:
            try:
                product = Product.objects.get(id=obj.productId)
                return product.name or ''
            except Product.DoesNotExist:
                return ''
        return ''

    def to_representation(self, instance):
        """字段映射：将模型字段映射为接口所需的字段名"""
        ret = super().to_representation(instance)

        # 映射 totalFee ← orderAmount
        ret['totalFee'] = instance.orderAmount
        # 映射 status ← orderStatus
        ret['status'] = instance.orderStatus
        # 映射 payTime ← paidTime
        ret['payTime'] = instance.paidTime

        return ret


# ============================================================================
# 创建订单序列化器
# ============================================================================

class OrderCreateSerializer(serializers.Serializer):
    """创建订单序列化器

    输入字段：productId, paymentType（1=支付宝, 2=微信）
    自动生成：orderNum、userId（由视图传入）
    """

    PAYMENT_TYPE_CHOICES = [
        (1, '支付宝'),
        (2, '微信'),
    ]

    productId = serializers.CharField(
        max_length=255,
        required=True,
        help_text='商品 ID',
    )
    paymentType = serializers.ChoiceField(
        choices=PAYMENT_TYPE_CHOICES,
        required=True,
        help_text='支付方式：1=支付宝, 2=微信',
    )

    def validate_productId(self, value):
        """校验商品是否存在"""
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value

    def create(self, validated_data):
        """创建订单记录

        自动生成 orderNum（订单号）、userId（当前用户）
        """
        user = self.context['request'].user
        product = Product.objects.get(id=validated_data['productId'])

        order = Orders.objects.create(
            orderNum=self._generate_order_num(),
            orderStatus='0',  # 0=待支付
            orderAmount=product.price,
            productId=validated_data['productId'],
            userId=str(user.id),
            buyCounts=1,
            createTime=timezone.now(),
        )

        return order

    @staticmethod
    def _generate_order_num() -> str:
        """生成订单号

        格式：YYYYMMDD + 8位随机字符（共16位）
        """
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:8].upper()
        return f'{date_part}{random_part}'


# ============================================================================
# 支付宝支付序列化器
# ============================================================================

class AlipayPaySerializer(serializers.Serializer):
    """支付宝支付序列化器

    输入字段：orderId
    返回：pay_url（支付宝支付链接）
    """

    orderId = serializers.IntegerField(required=True, help_text='订单 ID')

    def validate_orderId(self, value):
        """校验订单是否存在且属于当前用户"""
        try:
            order = Orders.objects.get(id=value)
        except Orders.DoesNotExist:
            raise serializers.ValidationError('订单不存在')

        user = self.context['request'].user
        if str(order.userId) != str(user.id):
            raise serializers.ValidationError('无权操作此订单')

        if order.orderStatus not in ('0',):
            raise serializers.ValidationError('订单状态不允许支付')

        return value


# ============================================================================
# 微信支付序列化器
# ============================================================================

class WxpayPaySerializer(serializers.Serializer):
    """微信支付序列化器

    输入字段：orderId
    返回：pay_params（微信调起支付参数）
    """

    orderId = serializers.IntegerField(required=True, help_text='订单 ID')

    def validate_orderId(self, value):
        """校验订单是否存在且属于当前用户"""
        try:
            order = Orders.objects.get(id=value)
        except Orders.DoesNotExist:
            raise serializers.ValidationError('订单不存在')

        user = self.context['request'].user
        if str(order.userId) != str(user.id):
            raise serializers.ValidationError('无权操作此订单')

        if order.orderStatus not in ('0',):
            raise serializers.ValidationError('订单状态不允许支付')

        return value

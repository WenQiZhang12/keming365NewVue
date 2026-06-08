# -*- coding: utf-8 -*-
"""
Payments App Models
从数据库实际字段逆向生成
"""

from django.db import models


class Orders(models.Model):
    """
    Orders - 订单表
    原表名: orders
    实际字段: id, order_num, user_id, product_id, product_name, order_amount, payment_type, order_status, paid_time, create_time
    """
    id = models.AutoField(primary_key=True, db_column='id')
    orderNum = models.CharField(max_length=255, null=True, blank=True, db_column='order_num')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    productId = models.CharField(max_length=255, null=True, blank=True, db_column='product_id')
    productName = models.CharField(max_length=255, null=True, blank=True, db_column='product_name')
    orderAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='order_amount')
    paymentType = models.IntegerField(null=True, blank=True, db_column='payment_type')
    orderStatus = models.CharField(max_length=255, null=True, blank=True, db_column='order_status')
    paidTime = models.DateTimeField(null=True, blank=True, db_column='paid_time')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'orders'

    def __str__(self):
        return str(self.id)


class Product(models.Model):
    """
    Product - 产品表
    原表名: product
    实际字段: id, name, price, description, image, create_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    name = models.CharField(max_length=255, null=True, blank=True, db_column='name')
    price = models.CharField(max_length=255, null=True, blank=True, db_column='price')
    description = models.TextField(null=True, blank=True, db_column='description')
    image = models.CharField(max_length=255, null=True, blank=True, db_column='image')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'product'

    def __str__(self):
        return str(self.name)

# -*- coding: utf-8 -*-
"""
Home App Models
从数据库实际字段逆向生成
"""

from django.db import models


class TbViewpager(models.Model):
    """
    TbViewpager - 轮播图表
    原表名: tb_viewpager
    实际字段: id, title, img_path, sort_order, flag, create_time, update_time, expire_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    imgPath = models.CharField(max_length=255, null=True, blank=True, db_column='img_path')
    sortOrder = models.IntegerField(null=True, blank=True, db_column='sort_order')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    expireTime = models.DateTimeField(null=True, blank=True, db_column='expire_time')

    class Meta:
        managed = False
        db_table = 'tb_viewpager'

    def __str__(self):
        return str(self.title)


class TbHot(models.Model):
    """
    TbHot - 热门推荐表
    原表名: tb_hot
    实际字段: id, class_id, cid, eid, calss_name, cname, ename, sort_order, status, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_id')
    cid = models.CharField(max_length=255, null=True, blank=True, db_column='cid')
    eid = models.CharField(max_length=255, null=True, blank=True, db_column='eid')
    calssName = models.CharField(max_length=255, null=True, blank=True, db_column='calss_name')
    cname = models.CharField(max_length=255, null=True, blank=True, db_column='cname')
    ename = models.CharField(max_length=255, null=True, blank=True, db_column='ename')
    sortOrder = models.IntegerField(null=True, blank=True, db_column='sort_order')
    status = models.IntegerField(null=True, blank=True, db_column='status')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_hot'

    def __str__(self):
        return str(self.id)


class TbIntro(models.Model):
    """
    TbIntro - 介绍表
    原表名: tb_intro
    实际字段: id, title, content, image, type, create_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    content = models.TextField(null=True, blank=True, db_column='content')
    image = models.CharField(max_length=255, null=True, blank=True, db_column='image')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'tb_intro'

    def __str__(self):
        return str(self.title)


class TbItemCat(models.Model):
    """
    TbItemCat - 分类表
    原表名: tb_item_cat
    实际字段: id, parent_id, name, status, sort_order, is_parent, tab_id, create_time, update_time, type
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    parentId = models.CharField(max_length=255, null=True, blank=True, db_column='parent_id')
    name = models.CharField(max_length=255, null=True, blank=True, db_column='name')
    status = models.IntegerField(null=True, blank=True, db_column='status')
    sortOrder = models.IntegerField(null=True, blank=True, db_column='sort_order')
    isParent = models.IntegerField(null=True, blank=True, db_column='is_parent')
    tabId = models.CharField(max_length=255, null=True, blank=True, db_column='tab_id')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    type = models.IntegerField(null=True, blank=True, db_column='type')

    class Meta:
        managed = False
        db_table = 'tb_item_cat'

    def __str__(self):
        return str(self.name)

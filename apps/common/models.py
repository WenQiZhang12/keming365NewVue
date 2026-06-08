# -*- coding: utf-8 -*-
"""
Common App Models
从数据库实际字段逆向生成
"""

from django.db import models


class TbClassify(models.Model):
    """
    TbClassify - 分类表
    原表名: tb_classify
    实际字段: id, class_name, sort_order, status, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    className = models.CharField(max_length=255, null=True, blank=True, db_column='class_name')
    sortOrder = models.IntegerField(null=True, blank=True, db_column='sort_order')
    status = models.IntegerField(null=True, blank=True, db_column='status')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_classify'

    def __str__(self):
        return str(self.className)


class TbClassInfo(models.Model):
    """
    TbClassInfo - 班级信息表
    原表名: tb_class_info
    实际字段: id, class_card, school_id, teacher_id, create_time, update_time, type
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    classCard = models.CharField(max_length=255, null=True, blank=True, db_column='class_card')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='school_id')
    teacherId = models.CharField(max_length=255, null=True, blank=True, db_column='teacher_id')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    type = models.IntegerField(null=True, blank=True, db_column='type')

    class Meta:
        managed = False
        db_table = 'tb_class_info'

    def __str__(self):
        return str(self.id)


class TbSchoolInfo(models.Model):
    """
    TbSchoolInfo - 学校信息表
    原表名: tb_school_info
    实际字段: id, name, type, sort_order, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    name = models.CharField(max_length=255, null=True, blank=True, db_column='name')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    sortOrder = models.IntegerField(null=True, blank=True, db_column='sort_order')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_school_info'

    def __str__(self):
        return str(self.name)


class Log(models.Model):
    """
    Log - 日志表
    原表名: log
    实际字段: log_id, type, title, remote_addr, request_uri, method, params, exception, operate_date, timeout, user_id, user_name
    """
    logId = models.CharField(max_length=255, null=True, blank=True, db_column='log_id')
    type = models.CharField(max_length=255, null=True, blank=True, db_column='type')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    remoteAddr = models.CharField(max_length=255, null=True, blank=True, db_column='remote_addr')
    requestUri = models.CharField(max_length=255, null=True, blank=True, db_column='request_uri')
    method = models.CharField(max_length=255, null=True, blank=True, db_column='method')
    params = models.CharField(max_length=255, null=True, blank=True, db_column='params')
    exception = models.CharField(max_length=255, null=True, blank=True, db_column='exception')
    operateDate = models.DateTimeField(null=True, blank=True, db_column='operate_date')
    timeout = models.CharField(max_length=255, null=True, blank=True, db_column='timeout')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    userName = models.CharField(max_length=255, null=True, blank=True, db_column='user_name')

    class Meta:
        managed = False
        db_table = 'log'

    def __str__(self):
        return str(self.title)

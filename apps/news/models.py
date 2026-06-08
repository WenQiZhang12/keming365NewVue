# -*- coding: utf-8 -*-
"""
News App Models
从数据库实际字段逆向生成
"""

from django.db import models


class News(models.Model):
    """
    News - 新闻表
    原表名: news
    实际字段: id, title, content, userid, time, browsetimes, priority, coverImg
    """
    id = models.AutoField(primary_key=True, db_column='id')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    content = models.TextField(null=True, blank=True, db_column='content')
    userid = models.IntegerField(null=True, blank=True, db_column='userid')
    time = models.DateTimeField(null=True, blank=True, db_column='time')
    browsetimes = models.IntegerField(null=True, blank=True, db_column='browsetimes')
    priority = models.IntegerField(null=True, blank=True, db_column='priority')
    coverImg = models.CharField(max_length=255, null=True, blank=True, db_column='coverImg')

    class Meta:
        managed = False
        db_table = 'news'

    def __str__(self):
        return str(self.title)

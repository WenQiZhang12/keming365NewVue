# -*- coding: utf-8 -*-
"""
Files App Models
从数据库实际字段逆向生成
"""

from django.db import models


class Video(models.Model):
    """
    Video - 视频表
    原表名: video
    实际字段: id, name, path, node_id, chapter_id, create_time
    """
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(max_length=255, null=True, blank=True, db_column='name')
    path = models.CharField(max_length=255, null=True, blank=True, db_column='path')
    nodeId = models.IntegerField(null=True, blank=True, db_column='node_id')
    chapterId = models.IntegerField(null=True, blank=True, db_column='chapter_id')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'video'

    def __str__(self):
        return str(self.name)

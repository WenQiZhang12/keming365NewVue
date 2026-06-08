# -*- coding: utf-8 -*-
"""
Comments App Models
从数据库实际字段逆向生成
"""

from django.db import models


class TbItemComment(models.Model):
    """
    TbItemComment - 评论表
    原表名: tb_item_comment
    实际字段: id, userid, curriculum_id, experiment_id, comment_content, create_time, update_time, status, update_id
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    userid = models.CharField(max_length=255, null=True, blank=True, db_column='userid')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_id')
    commentContent = models.CharField(max_length=255, null=True, blank=True, db_column='comment_content')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    status = models.IntegerField(null=True, blank=True, db_column='status')
    updateId = models.CharField(max_length=255, null=True, blank=True, db_column='update_id')

    class Meta:
        managed = False
        db_table = 'tb_item_comment'

    def __str__(self):
        return str(self.id)

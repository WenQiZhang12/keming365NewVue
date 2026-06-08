# -*- coding: utf-8 -*-
"""
Courses App Models
从数据库实际字段逆向生成
"""

import uuid
from django.db import models


class TbCurriculum(models.Model):
    """
    TbCurriculum - 课程表
    原表名: tb_curriculum
    实际字段: id, classify_id, status, curriculum_name, create_time, update_time, sort_order, price
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    classifyId = models.CharField(max_length=255, null=True, blank=True, db_column='classify_id')
    status = models.IntegerField(null=True, blank=True, db_column='status')
    curriculumName = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_name')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    sortOrder = models.CharField(max_length=255, null=True, blank=True, db_column='sort_order')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='price')

    class Meta:
        managed = False
        db_table = 'tb_curriculum'

    def __str__(self):
        return str(self.curriculumName)


class Chapter(models.Model):
    """
    Chapter - 章节表
    原表名: chapter
    实际字段: id, title, type, curriculum_id, pdfPath, order, create_time
    """
    id = models.AutoField(primary_key=True, db_column='id')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    pdfPath = models.CharField(max_length=255, null=True, blank=True, db_column='pdfPath')
    order = models.IntegerField(null=True, blank=True, db_column='order')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'chapter'

    def __str__(self):
        return str(self.title)


class TbExperiment(models.Model):
    """
    TbExperiment - 实验表
    原表名: tb_experiment
    实际字段: id, parent_id, title, publisher, sell_point, price, image, status, create_time, updated_time, appli_id, type, chapter_id, node_id
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    parentId = models.CharField(max_length=255, null=True, blank=True, db_column='parent_id')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    publisher = models.CharField(max_length=255, null=True, blank=True, db_column='publisher')
    sellPoint = models.CharField(max_length=255, null=True, blank=True, db_column='sell_point')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='price')
    image = models.CharField(max_length=255, null=True, blank=True, db_column='image')
    status = models.CharField(max_length=255, null=True, blank=True, db_column='status')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updatedTime = models.DateTimeField(null=True, blank=True, db_column='updated_time')
    appliId = models.CharField(max_length=255, null=True, blank=True, db_column='appli_id')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    chapterId = models.IntegerField(null=True, blank=True, db_column='chapter_id')
    nodeId = models.IntegerField(null=True, blank=True, db_column='node_id')
    # classifyId 对应 parent_id 字段，已由 parentId 字段覆盖

    class Meta:
        managed = False
        db_table = 'tb_experiment'

    def __str__(self):
        return str(self.title)


class TbExperimentReport(models.Model):
    """
    TbExperimentReport - 实验报告表
    原表名: tb_experiment_report
    实际字段: id, file_name, type, upload_num, create_time, update_time, user_id, class_Id, curriculum_id, experiment_id, un, report_score
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    fileName = models.CharField(max_length=255, null=True, blank=True, db_column='file_name')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    uploadNum = models.IntegerField(null=True, blank=True, db_column='upload_num')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_Id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_id')
    un = models.CharField(max_length=255, null=True, blank=True, db_column='un')
    reportScore = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='report_score')

    class Meta:
        managed = False
        db_table = 'tb_experiment_report'

    def __str__(self):
        return str(self.id)


class TbRecordInfo(models.Model):
    """
    TbRecordInfo - 记录信息表
    原表名: tb_record_info
    实际字段: id, curriculum_id, experiment_id, pass_num, browse_num, operate_num, flag, create_time, update_time, excellent, well, qualified, unQualified
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id', default=uuid.uuid4)
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_id')
    passNum = models.IntegerField(null=True, blank=True, db_column='pass_num')
    browseNum = models.IntegerField(null=True, blank=True, db_column='browse_num')
    operateNum = models.IntegerField(null=True, blank=True, db_column='operate_num')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    excellent = models.IntegerField(null=True, blank=True, db_column='excellent')
    well = models.IntegerField(null=True, blank=True, db_column='well')
    qualified = models.IntegerField(null=True, blank=True, db_column='qualified')
    unQualified = models.IntegerField(null=True, blank=True, db_column='unQualified')

    class Meta:
        managed = False
        db_table = 'tb_record_info'

    def __str__(self):
        return str(self.id)


class Node(models.Model):
    """
    Node - 节点表
    原表名: node
    实际字段: id, title, order, chapter_id, pptpath, create_time
    """
    id = models.AutoField(primary_key=True, db_column='id')
    title = models.CharField(max_length=255, null=True, blank=True, db_column='title')
    order = models.IntegerField(null=True, blank=True, db_column='order')
    chapterId = models.IntegerField(null=True, blank=True, db_column='chapter_id')
    pptpath = models.CharField(max_length=255, null=True, blank=True, db_column='pptpath')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'node'

    def __str__(self):
        return str(self.title)


class UserCurriculum(models.Model):
    """
    UserCurriculum - 用户课程关联表
    原表名: user_curriculum
    实际字段: id, user_id, curriculum_id, account_type, flag, create_time, update_time, expiration_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    accountType = models.IntegerField(null=True, blank=True, db_column='account_type')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    expirationTime = models.DateTimeField(null=True, blank=True, db_column='expiration_time')

    class Meta:
        managed = False
        db_table = 'user_curriculum'

    def __str__(self):
        return str(self.id)


class UserExperiment(models.Model):
    """
    UserExperiment - 用户实验关联表
    原表名: user_experiment
    实际字段: id, user_id, curriculum_id, experiment_id, account_type, experiment_type, flag, create_time, update_time, expiration_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_id')
    accountType = models.IntegerField(null=True, blank=True, db_column='account_type')
    experimentType = models.IntegerField(null=True, blank=True, db_column='experiment_type')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    expirationTime = models.DateTimeField(null=True, blank=True, db_column='expiration_time')

    class Meta:
        managed = False
        db_table = 'user_experiment'

    def __str__(self):
        return str(self.id)


class SchoolCurriculum(models.Model):
    """
    SchoolCurriculum - 学校课程关联表
    原表名: school_curriculum
    实际字段: id, school_id, curriculum_id, classify_id, flag, create_time, update_time, expiration_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='school_id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    classifyId = models.CharField(max_length=255, null=True, blank=True, db_column='classify_id')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    expirationTime = models.DateTimeField(null=True, blank=True, db_column='expiration_time')

    class Meta:
        managed = False
        db_table = 'school_curriculum'

    def __str__(self):
        return str(self.id)


class SchoolExperiment(models.Model):
    """
    SchoolExperiment - 学校实验关联表
    原表名: school_experiment
    实际字段: id, school_id, curriculum_id, experiment_id, experiment_type, flag, create_time, update_time, expiration_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='school_id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_id')
    experimentType = models.IntegerField(null=True, blank=True, db_column='experiment_type')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')
    expirationTime = models.DateTimeField(null=True, blank=True, db_column='expiration_time')

    class Meta:
        managed = False
        db_table = 'school_experiment'

    def __str__(self):
        return str(self.id)

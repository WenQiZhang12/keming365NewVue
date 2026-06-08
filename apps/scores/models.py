# -*- coding: utf-8 -*-
"""
Scores App Models
从数据库实际字段逆向生成
"""

from django.db import models


class TbExperimentScore(models.Model):
    """
    TbExperimentScore - 实验评分表
    原表名: tb_experiment_score
    实际字段: id, id_card, user_id, class_Id, curriculum_id, experiment_id, un, operation_score, experiment_num, flag, report_score, score_sum, pdf_path, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    idCard = models.CharField(max_length=255, null=True, blank=True, db_column='id_card')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_Id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_id')
    un = models.CharField(max_length=255, null=True, blank=True, db_column='un')
    operationScore = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='operation_score')
    experimentNum = models.IntegerField(null=True, blank=True, db_column='experiment_num')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    reportScore = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='report_score')
    scoreSum = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='score_sum')
    pdfPath = models.CharField(max_length=255, null=True, blank=True, db_column='pdf_path')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_experiment_score'

    def __str__(self):
        return str(self.id)


class TbExperimentUsetime(models.Model):
    """
    TbExperimentUsetime - 实验用时表
    原表名: tb_experiment_usetime
    实际字段: id, cid, eid, user_Id, newUsetime, usetime, experiment_type, flag, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    cid = models.CharField(max_length=255, null=True, blank=True, db_column='cid')
    eid = models.CharField(max_length=255, null=True, blank=True, db_column='eid')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_Id')
    newUsetime = models.CharField(max_length=255, null=True, blank=True, db_column='newUsetime')
    usetime = models.CharField(max_length=255, null=True, blank=True, db_column='usetime')
    experimentType = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_type')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_experiment_usetime'

    def __str__(self):
        return str(self.id)


class TbPersonScore(models.Model):
    """
    TbPersonScore - 个人评分表
    原表名: tb_person_score
    实际字段: id, class_id, cid, eid, user_id, score, flag, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_id')
    cid = models.CharField(max_length=255, null=True, blank=True, db_column='cid')
    eid = models.CharField(max_length=255, null=True, blank=True, db_column='eid')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_id')
    score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='score')
    flag = models.CharField(max_length=255, null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_person_score'

    def __str__(self):
        return str(self.id)


class TbMechanicUserScore(models.Model):
    """
    TbMechanicUserScore - 技工用户评分表
    原表名: tb_mechanic_user_score
    实际字段: id, uid, un, experimentName, experimentId, score, create_time
    """
    id = models.AutoField(primary_key=True, db_column='id')
    uid = models.CharField(max_length=255, null=True, blank=True, db_column='uid')
    un = models.CharField(max_length=255, null=True, blank=True, db_column='un')
    experimentName = models.CharField(max_length=255, null=True, blank=True, db_column='experimentName')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experimentId')
    score = models.BigIntegerField(null=True, blank=True, db_column='score')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'tb_mechanic_user_score'

    def __str__(self):
        return str(self.id)


class TbWeightInfo(models.Model):
    """
    TbWeightInfo - 权重信息表
    原表名: tb_weight_info
    实际字段: id, school_Id, class_Id, experiment_Id, operation, report, create_id, create_time, update_id, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='school_Id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_Id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_Id')
    operation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='operation')
    report = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='report')
    createId = models.CharField(max_length=255, null=True, blank=True, db_column='create_id')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateId = models.CharField(max_length=255, null=True, blank=True, db_column='update_id')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_weight_info'

    def __str__(self):
        return str(self.id)


class TbExperimentRecord(models.Model):
    """
    TbExperimentRecord - 实验记录表
    原表名: tb_experiment_record
    实际字段: id, user_Id, school_Id, curriculum_Id, experiment_Id, class_id, record_num, browse_num, create_time, update_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='user_Id')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='school_Id')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculum_Id')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experiment_Id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_id')
    recordNum = models.IntegerField(null=True, blank=True, db_column='record_num')
    browseNum = models.IntegerField(null=True, blank=True, db_column='browse_num')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    updateTime = models.DateTimeField(null=True, blank=True, db_column='update_time')

    class Meta:
        managed = False
        db_table = 'tb_experiment_record'

    def __str__(self):
        return str(self.id)

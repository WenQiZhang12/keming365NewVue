# -*- coding: utf-8 -*-
"""
Accounts App Models
从数据库实际字段逆向生成
"""

from django.db import models


class TbUser(models.Model):
    """
    TbUser - 用户表
    原表名: tb_user
    实际字段: id, id_card, school_id, specialty_id, class_id, name, username, password, type, user_img, school_name, specialty_name, class_name, sex, email, telephone, account_type, create_time, position, expire_time, works_path, authority_id
    """

    @property
    def is_authenticated(self):
        """DRF 权限系统需要此属性"""
        return True

    @property
    def is_active(self):
        """DRF SessionAuthentication 需要此属性"""
        return True

    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    idCard = models.CharField(max_length=255, null=True, blank=True, db_column='id_card')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='school_id')
    specialtyId = models.CharField(max_length=255, null=True, blank=True, db_column='specialty_id')
    classId = models.CharField(max_length=255, null=True, blank=True, db_column='class_id')
    name = models.CharField(max_length=255, null=True, blank=True, db_column='name')
    username = models.CharField(max_length=255, null=True, blank=True, db_column='username')
    password = models.CharField(max_length=255, null=True, blank=True, db_column='password')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    userImg = models.CharField(max_length=255, null=True, blank=True, db_column='user_img')
    schoolName = models.CharField(max_length=255, null=True, blank=True, db_column='school_name')
    specialtyName = models.CharField(max_length=255, null=True, blank=True, db_column='specialty_name')
    className = models.CharField(max_length=255, null=True, blank=True, db_column='class_name')
    sex = models.IntegerField(null=True, blank=True, db_column='sex')
    email = models.CharField(max_length=255, null=True, blank=True, db_column='email')
    telephone = models.CharField(max_length=255, null=True, blank=True, db_column='telephone')
    accountType = models.IntegerField(null=True, blank=True, db_column='account_type')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')
    position = models.CharField(max_length=255, null=True, blank=True, db_column='position')
    expireTime = models.DateTimeField(null=True, blank=True, db_column='expire_time')
    worksPath = models.CharField(max_length=255, null=True, blank=True, db_column='works_path')
    authorityId = models.CharField(max_length=255, null=True, blank=True, db_column='authority_id')

    class Meta:
        managed = False
        db_table = 'tb_user'

    def __str__(self):
        return str(self.name)


class Jwtinfo(models.Model):
    """
    Jwtinfo - JWT 密钥信息表
    原表名: jwtinfo
    实际字段: issueId, schoolId, curriculumId, experimentId, userId, secret, aeskey, flag, create_time
    """
    issueId = models.BigIntegerField(null=True, blank=True, db_column='issueId')
    schoolId = models.CharField(max_length=255, null=True, blank=True, db_column='schoolId')
    curriculumId = models.CharField(max_length=255, null=True, blank=True, db_column='curriculumId')
    experimentId = models.CharField(max_length=255, null=True, blank=True, db_column='experimentId')
    userId = models.CharField(max_length=255, null=True, blank=True, db_column='userId')
    secret = models.CharField(max_length=255, null=True, blank=True, db_column='secret')
    aeskey = models.CharField(max_length=255, null=True, blank=True, db_column='aeskey')
    flag = models.IntegerField(null=True, blank=True, db_column='flag')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'jwtinfo'

    def __str__(self):
        return str(self.issueId)


class TbMechanicUser(models.Model):
    """
    TbMechanicUser - 技工用户表
    原表名: tb_mechanic_user
    实际字段: id, un, type, create_time
    """
    id = models.CharField(primary_key=True, max_length=255, db_column='id')
    un = models.CharField(max_length=255, null=True, blank=True, db_column='un')
    type = models.IntegerField(null=True, blank=True, db_column='type')
    createTime = models.DateTimeField(null=True, blank=True, db_column='create_time')

    class Meta:
        managed = False
        db_table = 'tb_mechanic_user'

    def __str__(self):
        return str(self.id)

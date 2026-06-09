# -*- coding: utf-8 -*-
"""
apps.accounts.serializers - 用户与账户 序列化器
"""

import random
import re

from django.contrib.auth.hashers import make_password, check_password
import hashlib
from django.utils import timezone

from rest_framework import serializers

from apps.accounts.models import TbUser
from utils.exceptions import BusinessError
from utils.sms import sms_client


# ============================================================================
# 辅助函数
# ============================================================================

def _validate_telephone(value):
    """校验手机号格式（中国大陆 11 位）"""
    if not re.match(r'^1[3-9]\d{9}$', value):
        raise serializers.ValidationError('手机号格式不正确')
    return value


# ============================================================================
# 注册
# ============================================================================

class UserRegisterSerializer(serializers.Serializer):
    """用户注册序列化器"""

    username = serializers.CharField(max_length=255, required=True, help_text='用户名')
    password = serializers.CharField(
        max_length=255, required=True, write_only=True, help_text='密码',
    )
    name = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text='姓名')
    telephone = serializers.CharField(
        max_length=255, required=False, allow_blank=True, help_text='手机号',
        validators=[_validate_telephone],
    )
    type = serializers.IntegerField(default=0, required=False, help_text='用户类型（0=学生, 1=教师, 2=管理员）')

    def validate_type(self, value):
        if value not in (0, 1, 2):
            raise serializers.ValidationError('用户类型无效（0=学生, 1=教师, 2=管理员）')
        return value

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        # 检查用户名是否已存在
        if TbUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value.strip()

    def validate(self, attrs):
        # 生成主键 ID（时间戳 + 随机数）
        import uuid
        attrs['id'] = str(uuid.uuid4()).replace('-', '')[:32]
        # 密码加密
        attrs['password'] = make_password(attrs['password'])
        # 设置创建时间
        attrs['createTime'] = timezone.now()
        return attrs

    def create(self, validated_data):
        # Use raw SQL to avoid Django ORM inserting columns not in the actual table
        from django.db import connection
        id_val = validated_data.get('id')
        username = validated_data.get('username')
        password = validated_data.get('password')
        name_val = validated_data.get('name', '')
        telephone = validated_data.get('telephone', '')
        create_time = validated_data.get('createTime')
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO tb_user (id, username, password, name, telephone, create_time) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                [id_val, username, password, name_val, telephone, create_time]
            )
        return TbUser(**validated_data)


# ============================================================================
# 登录
# ============================================================================

class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""

    username = serializers.CharField(max_length=255, required=True, help_text='用户名')
    password = serializers.CharField(
        max_length=255, required=True, write_only=True, help_text='密码',
    )

    _user = None  # 缓存校验通过的用户对象

    @property
    def user(self):
        return self._user

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        return value.strip()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = TbUser.objects.get(username=username)
        except TbUser.DoesNotExist:
            raise serializers.ValidationError('用户名或密码错误')

        if not user.password:
            raise serializers.ValidationError('用户名或密码错误')

        stored = user.password

        # 1. 先尝试 Django 原生格式（pbkdf2_sha256 等）
        try:
            if check_password(password, stored):
                self._user = user
                return attrs
        except (ValueError, TypeError):
            pass  # 非 Django 格式的哈希，跳过

        # 2. 兼容 Java 后端的 MD5 密码格式
        #    Java 前端登录时先做 MD5，后端直接存储 MD5 值
        #    Django 前端直接发明文，所以这里对明文做 MD5 后比较
        md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        if stored == md5_hash:
            self._user = user
            return attrs

        # 3. 也兼容存储的密码本身就是明文（极少数情况）
        if stored == password:
            self._user = user
            return attrs

        raise serializers.ValidationError('用户名或密码错误')


# ============================================================================
# 个人信息
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器（只读）"""

    id = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    telephone = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    type = serializers.IntegerField(read_only=True)
    schoolName = serializers.CharField(read_only=True)
    className = serializers.CharField(read_only=True)
    sex = serializers.IntegerField(read_only=True)
    userImg = serializers.CharField(read_only=True)
    createTime = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = TbUser
        fields = [
            'id', 'username', 'name', 'telephone', 'email', 'type',
            'schoolName', 'className', 'sex', 'userImg', 'createTime',
        ]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """用户个人信息更新序列化器"""

    name = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text='姓名')
    telephone = serializers.CharField(
        max_length=255, required=False, allow_blank=True, help_text='手机号',
        validators=[_validate_telephone],
    )
    email = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text='邮箱')
    sex = serializers.IntegerField(required=False, help_text='性别（0=未知, 1=男, 2=女）')
    userImg = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text='头像 URL')

    class Meta:
        model = TbUser
        fields = [
            'name', 'telephone', 'email', 'sex', 'userImg',
        ]

    def validate_sex(self, value):
        if value not in (0, 1, 2):
            raise serializers.ValidationError('性别值无效（0=未知, 1=男, 2=女）')
        return value


# ============================================================================
# 修改密码
# ============================================================================

class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""

    oldPassword = serializers.CharField(
        max_length=255, required=True, write_only=True, help_text='旧密码',
    )
    newPassword = serializers.CharField(
        max_length=255, required=True, write_only=True, help_text='新密码',
    )

    def validate_newPassword(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('新密码长度不能少于 6 位')
        return value


# ============================================================================
# 发送短信验证码
# ============================================================================

class SendSmsSerializer(serializers.Serializer):
    """发送短信验证码序列化器"""

    telephone = serializers.CharField(
        max_length=255, required=True, help_text='手机号',
        validators=[_validate_telephone],
    )

    _code = None  # 生成的验证码

    @property
    def code(self):
        return self._code

    def validate(self, attrs):
        telephone = attrs.get('telephone')
        # 生成 6 位随机验证码
        self._code = f'{random.randint(100000, 999999)}'
        # 发送短信（开发环境打印日志）
        sms_client.send_verification_code(telephone, self._code)
        return attrs

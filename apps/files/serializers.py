# -*- coding: utf-8 -*-
"""
apps.files.serializers - 文件管理 序列化器
"""

from rest_framework import serializers

from apps.files.models import Video


class FileUploadSerializer(serializers.Serializer):
    """文件上传序列化器"""

    file = serializers.FileField(
        help_text='上传文件',
    )
    type = serializers.ChoiceField(
        choices=[
            ('image', '图片'),
            ('pdf', 'PDF'),
            ('video', '视频'),
            ('ppt', 'PPT'),
            ('other', '其他'),
        ],
        help_text='文件类型',
        required=False,
    )
    experimentId = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='关联的实验 ID（上传实验报告时传入）',
    )


class PreviewSerializer(serializers.Serializer):
    """文件预览信息序列化器"""

    id = serializers.IntegerField(read_only=True)
    fileName = serializers.CharField(
        source='get_file_name',
        read_only=True,
        help_text='文件名',
    )
    fileType = serializers.CharField(
        source='get_file_type',
        read_only=True,
        help_text='文件类型',
    )
    fileSize = serializers.CharField(
        source='get_file_size',
        read_only=True,
        help_text='文件大小',
    )
    fileUrl = serializers.CharField(
        source='get_file_url',
        read_only=True,
        help_text='文件 URL',
    )
    createTime = serializers.DateTimeField(
        source='created_at',
        read_only=True,
        help_text='创建时间',
    )

    def get_file_name(self, obj):
        raise NotImplementedError('使用实际对象时请实现此方法')

    def get_file_type(self, obj):
        raise NotImplementedError('使用实际对象时请实现此方法')

    def get_file_size(self, obj):
        raise NotImplementedError('使用实际对象时请实现此方法')

    def get_file_url(self, obj):
        raise NotImplementedError('使用实际对象时请实现此方法')


class VideoSerializer(serializers.ModelSerializer):
    """视频信息序列化器"""

    videoName = serializers.CharField(source='name', read_only=True, help_text='视频名称')
    videoUrl = serializers.CharField(source='path', read_only=True, help_text='视频 URL')
    videoType = serializers.SerializerMethodField(help_text='视频类型')
    duration = serializers.SerializerMethodField(help_text='视频时长')
    createTime = serializers.DateTimeField(
        source='createTime',
        read_only=True,
        help_text='创建时间',
    )

    class Meta:
        model = Video
        fields = [
            'id',
            'videoName',
            'videoUrl',
            'videoType',
            'duration',
            'createTime',
        ]

    def get_videoType(self, obj):
        """从路径推断视频类型"""
        if obj.path:
            ext = obj.path.rsplit('.', 1)[-1].lower() if '.' in obj.path else ''
            ext_map = {
                'mp4': 'mp4',
                'avi': 'avi',
                'mov': 'mov',
                'wmv': 'wmv',
                'flv': 'flv',
                'mkv': 'mkv',
                'webm': 'webm',
            }
            return ext_map.get(ext, 'unknown')
        return 'unknown'

    def get_duration(self, obj):
        """视频时长（从数据库暂取 None，后续可对接媒体分析）"""
        return None

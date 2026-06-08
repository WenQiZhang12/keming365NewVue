# -*- coding: utf-8 -*-
"""
utils.file_convert - 文件转换工具

提供 Office 文档转 PDF、图片处理等通用功能。
后续接入 LibreOffice / unoconv 等工具。
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_to_pdf(source_path: str | Path, output_path: str | Path = None) -> Path:
    """
    将 Office 文档转换为 PDF

    Args:
        source_path: 源文件路径
        output_path: 输出路径（默认与源文件同目录，同名 .pdf）

    Returns:
        Path: 输出 PDF 路径
    """
    raise NotImplementedError('文件转换功能待实现')


def resize_image(source_path: str | Path, output_path: str | Path = None,
                 width: int = None, height: int = None, quality: int = 85) -> Path:
    """
    调整图片尺寸

    Args:
        source_path: 源图片路径
        output_path: 输出路径
        width:       目标宽度
        height:      目标高度
        quality:     图片质量 (1-100)

    Returns:
        Path: 输出图片路径
    """
    raise NotImplementedError('图片处理功能待实现')

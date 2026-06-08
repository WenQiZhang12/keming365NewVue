# -*- coding: utf-8 -*-
"""
Settings 包初始化

根据 DJANGO_ENV 环境变量自动选择配置：
  - dev  → config.settings.dev（默认）
  - prod → config.settings.prod
"""
import os

env = os.environ.get('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *  # noqa: F401, F403
else:
    from .dev import *  # noqa: F401, F403

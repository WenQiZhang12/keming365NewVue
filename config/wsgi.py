# -*- coding: utf-8 -*-
"""
WSGI config for keming365 project.

用于传统 WSGI 服务器（如 Gunicorn）部署。
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

import pymysql, sys
sys.path.insert(0, r'D:\ZWQProject\365\keming365-backend')

# 直接用 Django 的 ORM 设置密码
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.accounts.models import TbUser
from django.contrib.auth.hashers import make_password

try:
    user = TbUser.objects.get(username='admin')
    user.password = make_password('admin123')
    user.type = 2
    user.account_type = 2
    user.save()
    print('OK - 密码已更新')
    # 验证
    from django.contrib.auth.hashers import check_password
    user2 = TbUser.objects.get(username='admin')
    print('Verify:', check_password('admin123', user2.password))
except Exception as e:
    print('Error:', e)

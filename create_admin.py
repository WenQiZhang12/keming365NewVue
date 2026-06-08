#!/usr/bin/env python3
import os, sys
sys.path.insert(0, 'D:\\ZWQProject\\365\\keming365-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
django.setup()

import pymysql
from uuid import uuid4
from datetime import datetime
from django.contrib.auth.hashers import make_password

pw = make_password('admin123')
uid = uuid4().hex[:32]
now = datetime.now()

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='new365')
cursor = conn.cursor()

# 先删旧的admin
cursor.execute("DELETE FROM tb_user WHERE username='admin'")

cursor.execute(
    'INSERT INTO tb_user (id, username, password, name, type, account_type, create_time) VALUES (%s,%s,%s,%s,%s,%s,%s)',
    (uid, 'admin', pw, '管理员', 2, 2, now)
)
conn.commit()
cursor.close()
conn.close()
print('OK - admin / admin123')

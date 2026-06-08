import pymysql

# Django PBKDF2 密码 (admin123)
# 用 Django 的 make_password 生成的
django_pw = 'pbkdf2_sha256$600000$dGXpUL3JoSfZ$R5VHZD9+l3Cxy50r5EXuMsLDCJgPsdmT8/nxGDLQ3mM='

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='new365')
cur = conn.cursor()
cur.execute("UPDATE tb_user SET password=%s, type=2, account_type=2 WHERE username='admin'", (django_pw,))
print('Updated:', cur.rowcount)
conn.commit()
cur.close()
conn.close()

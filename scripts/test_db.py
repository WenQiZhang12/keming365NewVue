import MySQLdb

passwords = ['', 'root', '123456', 'admin', 'password', 'keming', 'keming365', '1234', 'mysql', 'Root123', 'root123', 'Root@123', 'Aa123456', 'Abc123']
for p in passwords:
    try:
        conn = MySQLdb.connect(host='localhost', user='root', password=p)
        print(f'SUCCESS: password="{p}"')
        conn.close()
        break
    except Exception as e:
        err = str(e).split('\n')[0]
        print(f'FAIL: password="{p}" - {err}')
else:
    print('All passwords failed')

import sys; sys.path.insert(0,'.')
import django,os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.dev'
django.setup()
from rest_framework.test import APIClient
c = APIClient()
r = c.post('/api/v1/accounts/auth/login/', {'username':'admin','password':'admin123'}, format='json')
print('Status:', r.status_code)
print('Data:', r.data)

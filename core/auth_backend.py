# auth_backend.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connection

class SQLServerAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        with connection.cursor() as cursor:
            cursor.execute("SELECT email,telefono FROM core_cliente WHERE email=%s AND telefono=%s", [username, password])
            row = cursor.fetchone()
            if row:
                user, created = User.objects.get_or_create(username=username)
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

from django.apps import AppConfig
from django.core.cache import cache

import os


class DataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            from .models import User
            cache.set('cache::user_email_list', list(User.objects.values_list('email', flat=True)))
            cache.set('cache::email_name_list', list(User.objects.values_list('email', 'name')))

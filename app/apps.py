import os

from django.apps import AppConfig

# from gensim.models import KeyedVectors

CUR_DIR_PATH = os.getcwd()


class FiltersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'



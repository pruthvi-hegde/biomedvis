import os
from django.apps import AppConfig
# from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

CUR_DIR_PATH = os.getcwd()


class FiltersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'filter'
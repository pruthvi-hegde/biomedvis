import os
from django.apps import AppConfig
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

CUR_DIR_PATH = os.getcwd()


class FiltersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'filter'
    # Only for development purposes.
    # if os.environ.get('RUN_MAIN') == 'true':
    try:
        model = KeyedVectors.load_word2vec_format(
            CUR_DIR_PATH + '/filter/static/mlmodels/BioWordVec_PubMed_MIMICIII_d200.txt', binary=True, limit=10000)
    except:
        print("Model could not be loaded")


    # sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

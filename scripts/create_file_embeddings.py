import os
import json
from sentence_transformers import SentenceTransformer
from flair.embeddings import TransformerWordEmbeddings
from flair.data import Sentence
from gensim.models import KeyedVectors
import numpy as np

CUR_DIR_PATH = os.curdir()

# change model according to you needs.
sentence_transformers_model = SentenceTransformer('all-MiniLM-L6-v2')
biowordvec_model = KeyedVectors.load_word2vec_format(
              CUR_DIR_PATH + '/filter/static/mlmodels/BioWordVec_PubMed_MIMICIII_d200.txt', binary=True, limit=1000000)
embedding = TransformerWordEmbeddings("cambridgeltl/SapBERT-from-PubMedBERT-fulltext")


def get_files(filepath):
    file_set = set()
    for base, dirs, files in os.walk(filepath):
        for filename in files:
            file_set.add(base + '/' + filename)
    return file_set


def create_embeddings():
    files = get_files('../abstracts_title')
    all_data = []
    file_names = []

    for file in files:
        if os.path.getsize(file) != 0:
            with open(file, 'r') as f:
                content = f.read()
                all_data.append(content)
                file_names.append(file.split('/')[-1].replace('.txt', ''))
        else:
            print("File size is 0")
    sentence_embeddings = [np.mean(sentence_transformers_model.encode(all_data[i].split(". ")), axis=0).tolist() for i
                           in range(0, len(all_data))]

    # Create and save file according to your model
    result = dict(zip(file_names, sentence_embeddings))
    with open('../embeddings/sentence_transformer_average.json', 'w') as f:
        json.dump(result, f)
    print("wrote to a file")


if __name__ == "__main__":
    create_embeddings()


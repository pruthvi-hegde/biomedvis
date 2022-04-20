import asyncio
import nltk
import numpy as np
import numpy as np
import os
import os.path as path
import plotly.express as px
import re
from matplotlib import pyplot
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import TSNE
from sklearn.mixture import GaussianMixture
from string import punctuation

from filter.apps import FiltersConfig

CUR_DIR = os.path.basename(os.getcwd())


# sentence_transformer_model = FiltersConfig.sentence_transformer_model


def get_files(filepath):
    file_set = set()
    for base, dirs, files in os.walk(filepath):
        for filename in files:
            file_set.add(base + '/' + filename)
    return file_set


def get_mean_vector(model, words):
    # remove out-of-vocabulary words
    words = [word for word in words if word in model.vocab]
    if len(words) >= 1:
        return np.mean(model[words], axis=0)
    else:
        return []


def calculate_doc_average_word2vec(model, article_titles):
    all_words = []
    file_names = []
    for file in article_titles:
        file = path.join('../' + CUR_DIR + '/abstracts_title/', file.replace("/", "-") + '.txt')
        if os.path.getsize(file) != 0:
            with open(file, 'r') as f:
                content = f.read()
                all_words.append(preprocess_sentence_returns_list(content))
                file_names.append(str(file).split('/')[-1].replace(".txt", ""))
        else:
            print("File size is 0")

    # loop = asyncio.get_event_loop()

    doc_vectors = []
    for doc in all_words:
        vec = get_mean_vector(model, doc)
        if len(vec) > 0:
            doc_vectors.append(vec)

    tsne_model = TSNE(perplexity=5, n_components=2, init='pca', n_iter=1500, random_state=23)
    new_values = tsne_model.fit_transform(doc_vectors)
    # cluster_obj = cluster_documents()

    fig = px.scatter(new_values, x=0, y=1, hover_name=file_names, opacity=1)
    return fig


def preprocess_sentence_returns_list(text):
    stop_words = set(stopwords.words('english'))
    lem = nltk.stem.wordnet.WordNetLemmatizer()
    cleanr = re.compile('\[(.*?)\]')
    text = re.sub(cleanr, '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub("[0-9]{2}", '', text)
    text = text.replace('/', ' ')
    text = text.replace('\'', ' \' ')
    pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
    text = re.sub(pat, '', text)
    text = text.lower()

    words = text.split()
    text = ' '.join([lem.lemmatize(word) for word in words])
    # text = ' '.join(words)
    text = ' '.join([w for w in text.split() if len(w) > 1])
    text = text.replace('/`/', '')
    text = text.replace('/"/', '')
    text = text.replace("/'/", "")

    tokens = [token for token in word_tokenize(text) if token not in punctuation and token not in stop_words]
    return tokens


def cluster_documents():
    print("here")
    all_articles = []
    file_names = []
    for file in article_titles:
        file = path.join('../' + CUR_DIR + '/abstracts_title/', file.replace("/", "-") + '.txt')
        if os.path.getsize(file) != 0:
            with open(file, 'r') as f:
                content = f.read()
                all_articles.append(content)
                file_names.append(str(file).split('/')[-1].replace(".txt", ""))
        else:
            print("File size is 0")
    corpus_embeddings = sentence_transformer_model.encode(all_articles)
    print(corpus_embeddings)

    # Normalize the embeddings to unit length
    corpus_embeddings = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)

    # Perform kmean clustering
    clustering_model = AgglomerativeClustering(n_clusters=None, distance_threshold=1.5,
                                               memory='../')  # , affinity='cosine', linkage='average', distance_threshold=0.4)
    xff = clustering_model.fit_predict(corpus_embeddings)

    # cluster_assignment = clustering_model.labels_
    #
    # clustered_sentences = {}
    # art_name = []
    # for sentence_id, cluster_id in enumerate(cluster_assignment):
    #     if cluster_id not in clustered_sentences:
    #         clustered_sentences[cluster_id] = []
    #     clustered_sentences[cluster_id].append(ar_title[sentence_id])
    #     art_name.append(ar_title[sentence_id])
    #
    # counter = []
    # for i, cluster in clustered_sentences.items():
    #     print("Cluster ", i)
    #     print(cluster)
    #     print("")
    #     counter.append(i)

    return xff

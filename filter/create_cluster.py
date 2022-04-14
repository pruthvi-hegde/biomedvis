import os
import os.path as path
import re
from string import punctuation

import nltk
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.offline as py
import matplotlib.pyplot as plt


from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score



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
        mean_vector_of_article = np.mean(model[words], axis=0)
        return mean_vector_of_article
    else:
        return []


def calculate_doc_average_word2vec(model, article_titles):
    all_words = []
    file_names = []
    for file in article_titles:
        file = path.join('../visbiomed/abstracts_title/',
                         file.replace("/", "-") + '.txt')
        if os.path.getsize(file) != 0:
            with open(file, 'r') as f:
                content = f.read()
                all_words.append(preprocess_sentence_returns_list(content))
                file_names.append(str(file).split('/')[-1].replace(".txt", ""))
        else:
            print("File size is 0")
    # doc_vectors = np.empty((200,),float)
    doc_vectors = []
    for doc in all_words:
        vec = get_mean_vector(model, doc)
        if len(vec) > 0:
            doc_vectors.append(vec)
    doc_vectors = np.array(doc_vectors)
    tsne_model = TSNE(perplexity=5, n_components=2, init='pca', n_iter=1500, random_state=23, learning_rate='auto')
    new_values = tsne_model.fit_transform(doc_vectors)
    print(new_values)


    # distortions = []
    # inertias = []
    # mapping1 = {}
    # mapping2 = {}
    # Q = range(1, 10)
    # X = doc_vectors
    # for k in Q:
    #     # Building and fitting the model
    #     kmeanModel = KMeans(n_clusters=k).fit(X)
    #     kmeanModel.fit(X)
    #
    #     distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_,
    #                                         'euclidean'), axis=1)) / X.shape[0])
    #     inertias.append(kmeanModel.inertia_)
    #
    #     mapping1[k] = sum(np.min(cdist(X, kmeanModel.cluster_centers_,
    #                                    'euclidean'), axis=1)) / X.shape[0]
    #     mapping2[k] = kmeanModel.inertia_
    #
    # for key, val in mapping1.items():
    #     print(f'{key} : {val}')
    # plt.plot(Q, distortions, 'bx-')
    # plt.xlabel('Values of K')
    # plt.ylabel('Distortion')
    # plt.title('The Elbow Method using Distortion')
    # plt.show()
    # return plt

    # fig = px.scatter(new_values, x=0, y=1, hover_name=file_names, opacity=1)
    # return fig


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

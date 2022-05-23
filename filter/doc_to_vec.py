import json
import os
import re
from string import punctuation

import nltk
import numpy as np
import plotly.express as px
from nltk import word_tokenize
from nltk.corpus import stopwords
from umap import UMAP

nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

CUR_DIR = os.path.basename(os.getcwd())


class Doc2Vec:

    def __init__(self):
        f = open('embeddings/file_embeddings_sentence_split.json')
        self.data = json.load(f)

    def get_files(self, filepath):
        file_set = set()
        for base, dirs, files in os.walk(filepath):
            for filename in files:
                file_set.add(base + '/' + filename)
        return file_set

    def get_mean_vector(self, model, words):
        # remove out-of-vocabulary words
        words = [word for word in words if word in model.vocab]
        if len(words) >= 1:
            return np.mean(model[words], axis=0)
        else:
            return []

    def calculate_doc_average_word2vec(self, article_titles):
        if len(article_titles) < 236:
            article_embeddings = [self.data[title.replace('/', '-')] for title in article_titles]
        else:
            article_embeddings = list(self.data.values())
            article_titles = list(self.data.keys())
        # tsne_model = TSNE(perplexity=5, n_components=2, init='pca', n_iter=2500, random_state=45)
        umap_embeddings = UMAP(n_neighbors=5, n_components=2, metric='cosine', random_state=42)
        low_dim_values = umap_embeddings.fit_transform(article_embeddings)
        fig = px.scatter(low_dim_values, x=0, y=1, opacity=1, hover_name=article_titles)
        fig.update_traces(marker_color='#D64045')
        fig.update_layout(
            title="Embedding view of articles generated from BioWordVec",
            title_font_color='#666666',
            title_font_size=16,
            title_font_family='Calibri',
            margin=dict(l=5, r=5, b=30),
            xaxis_title='',
            yaxis_title='',
            xaxis=dict(
                showline=True,
                showgrid=True,
                linecolor='#666666',
                tickfont=dict(
                    family='poppins',
                    color='#666666'
                )
            ),
            yaxis=dict(  # attribures for y axis
                showline=True,
                showgrid=True,
                linecolor='#666666',
                tickfont=dict(
                    family='poppins',
                    color='#666666'
                )
            ),
            hoverlabel=dict(
                bgcolor="#ffffff",
                font_size=12,
                font_color="#141414",
                font_family="Calibri",
                bordercolor="#D64045",
            ),
            plot_bgcolor='white',
        )

        return fig

    def preprocess_sentence_returns_list(self, text):
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


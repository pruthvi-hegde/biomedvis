import json
import os
import re
from string import punctuation

import nltk
import plotly.express as px
import plotly.graph_objects as go
from nltk import word_tokenize
from nltk.corpus import stopwords

nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

CUR_DIR = os.path.basename(os.getcwd())


class Doc2Vec:

    def __init__(self, model_name):
        f = open(f'embeddings/low_dim/{model_name}_low_dim.json')
        self.data = json.load(f)

    def calculate_doc_average(self, article_titles):
        all_article_embeddings = list(self.data.values())
        all_article_titles = list(self.data.keys())
        fig = px.scatter(all_article_embeddings, x=0, y=1, opacity=1, hover_name=all_article_titles)
        fig.update_traces(marker_color='#2950b3', selector=dict(mode='markers'))
        if len(article_titles) < 236:
            selected_article_embeddings = [self.data[title] for title in article_titles]
            x, y = map(list, zip(*selected_article_embeddings))
            fig.update_traces(marker_color='#2950b3', selector=dict(mode='markers'), opacity=0.5)
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', hovertext=article_titles, showlegend=False,
                                     name='Selected',
                                     marker=dict(
                                         color='#ff0000',
                                     ),
                                     hoverlabel=dict(
                                         bgcolor="#ffffff",
                                         font_size=12,
                                         font_color="#141414",
                                         font_family="Calibri",
                                         bordercolor="#D64045",
                                     ),
                                     hovertemplate='<b>%{hovertext}<br></b><br>0=%{x}<br>1=%{y}'
                                     ))
        fig.update_layout(
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
                bordercolor="#204ab3",
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

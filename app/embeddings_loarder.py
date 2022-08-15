import json
import os

import nltk
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import CountVectorizer

nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

CUR_DIR = os.path.basename(os.getcwd())


class Doc2Vec:

    def __init__(self, model_name):
        f = open(f'embeddings/low_dimension/{model_name}_low_dim.json')
        self.data = json.load(f)

    def visualise_doc_embeddings(self, article_titles):
        all_article_embeddings = list(self.data.values())
        all_article_titles = list(self.data.keys())
        fig = px.scatter(all_article_embeddings, x=0, y=1, opacity=1, hover_name=all_article_titles)
        fig.update_traces(marker_color='#2950b3', selector=dict(mode='markers'))
        if len(article_titles) < 236:
            selected_article_embeddings = [self.data[title] for title in article_titles]
            x, y = map(list, zip(*selected_article_embeddings))
            # fig.update_traces(marker_color='#2950b3', selector=dict(mode='markers'), opacity=0.3)
            fig.update_traces(marker_color='#2950b3', selector=dict(mode='markers'), opacity=0.3)
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', hovertext=article_titles, showlegend=False,
                                     name='Selected',
                                     marker=dict(
                                         color='#E50914',
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

    def cluster_docs(self):
        metadata = open(
            '/Users/prush/PycharmProjects/thesis/biomedvis/articles_data/all_articles_with_thumbnail_metadata.json')
        papers = json.load(metadata)
        doc_titles = list(self.data.keys())
        embeddings = list(self.data.values())
        docs = [paper['article_title'] + '. ' + paper['abstract'] for paper in papers]
        doc_years = [paper['published_year'] for paper in papers]
        # umap_data = umap.UMAP(n_neighbors=5,
        #                       n_components=2,
        #                       metric='cosine', random_state=42).fit_transform(embeddings)

        cluster = DBSCAN(eps=0.3, min_samples=2, metric='euclidean', metric_params=None, algorithm='brute').fit(
            embeddings)

        result = pd.DataFrame(embeddings, columns=['x', 'y'])
        result['labels'] = cluster.labels_
        result['titles'] = doc_titles
        result['years'] = doc_years

        docs_df = pd.DataFrame(docs, columns=["Doc"])
        docs_df['Topic'] = cluster.labels_
        docs_df['Titles'] = doc_titles
        docs_df['Years'] = doc_years
        docs_df['Doc_ID'] = range(len(docs_df))
        docs_per_topic = docs_df.groupby(['Topic'], as_index=False).agg({'Doc': ' '.join, 'Years': set, 'Titles': len})
        index = list(docs_per_topic.Years)
        years_topic_wise = {i - 1: list(index) for i, index in enumerate(index)}
        return result, docs, cluster, docs_df, docs_per_topic, years_topic_wise

    def c_tf_idf(self, documents, m, ngram_range=(1, 2)):
        count = CountVectorizer(ngram_range=ngram_range, stop_words="english").fit(documents)
        t = count.transform(documents).toarray()
        w = t.sum(axis=1)
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        return tf_idf, count

    def extract_top_n_words_per_topic(self, tf_idf, count, docs_per_topic, n):
        words = count.get_feature_names()
        labels = list(docs_per_topic.Topic)
        tf_idf_transposed = tf_idf.T
        indices = tf_idf_transposed.argsort()[:, -n:]
        top_n_words = {label: [words[j] for j in indices[i]][::-1] for i, label in enumerate(labels)}
        return top_n_words

    def inititate_cluster_docs(self, article_titles):
        result, docs, cluster, docs_df, docs_per_topic, years_topic_wise = self.cluster_docs()
        tf_idf, count = self.c_tf_idf(docs_per_topic.Doc.values, m=len(docs))
        top_n_words = self.extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=5)
        outliers = result.loc[result.labels == -1, :]
        clustered = result.loc[result.labels != -1, :]
        clustered_years = [value for key, value in years_topic_wise.items() if key != 1]
        top_terms = top_n_words

        for key, a in top_terms.items():
            k = []
            for i in a:
                for j in a:
                    if i != j and i in j:
                        k.append(i)

            r = list(filter(lambda i: i not in k, a))
            top_terms[key] = r

        for b in clustered_years:
            k = b
            k = b.sort()

        topic_years = ['.'.join(str(e) for e in years_topic_wise[item]) for item in clustered.labels]
        topic_years_outliers = ['.'.join(str(e) for e in years_topic_wise[item]) for item in outliers.labels]

        top_terms_docs = ['.'.join(str(e) for e in top_terms[item]) for item in clustered.labels]
        top_terms_docs_outliers = ['.'.join(str(e) for e in top_terms[item]) for item in outliers.labels]

        color_discrete_sequence = ["#CD6155", '#9a4979', '#62b9cc', '#873600', '#117A65', '#de881f', '#CB4335',
                                   '#c43f93', '#3dccd1', '#e07141', '#e041a0', '#0f00cd', '#ffa700', '#d62d20',
                                   '#008844', '#72bd68', '#ba434f', '#48c2ba', '#945edb', '#e206cb', '#cfd63c',
                                   '#ca3bf9', '#bfc403', '#ba0e37', '#9aa655', '#8e471b', '#473100',
                                   '#fda025', '#21618C', '#6C3483', '#91ca1e', '#EB984E', '#239B56', '#1A5276']

        clustered['Publication Years'] = topic_years
        clustered['Topic Words'] = top_terms_docs
        clustered['Cluster Number'] = clustered.labels
        df1 = pd.DataFrame({'doc_terms_outliers': top_terms_docs_outliers, 'doc_years_outliers': topic_years_outliers})
        fig = px.scatter(clustered, x='x', y='y', hover_name='titles', color='Topic Words',
                         # labels={"Topic Words" : "Topics"},
                         hover_data=['Publication Years', 'Cluster Number'],
                         color_discrete_sequence=color_discrete_sequence)

        fig.add_trace(go.Scatter(x=outliers.x, y=outliers.y, customdata=df1, mode='markers', hovertext=outliers.titles,
                                 name='outliers',
                                 marker=dict(
                                     color='#BDBDBD',
                                 ),
                                 hoverlabel=dict(
                                     bgcolor="#ffffff",
                                     font_size=12,
                                     font_color="#141414",
                                     font_family="Calibri",
                                     bordercolor="#BDBDBD",
                                 ),
                                 hovertemplate='<b>%{hovertext}<br></b><br><br>Topic= %{customdata[0]}</br>Years = %{customdata[1]}<br>'
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

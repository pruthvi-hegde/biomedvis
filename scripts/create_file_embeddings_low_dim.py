import json

import umap
from sentence_transformers import SentenceTransformer
from umap import UMAP
from sentence_transformers import util


def create_low_dim_embeddings_for_models(model_name):
    with open('../articles_data/all_articles_with_thumbnail_metadata_retired.json') as f:
        papers = json.load(f)

    # We then load the allenai-specter model with SentenceTransformers
    model = SentenceTransformer(model_name)
    model_name = model_name.replace('-', '_').lower()

    # To encode the papers, we must combine the title and the abstracts to a single string
    article_texts = [paper['article_title'] + '[SEP]' + paper['abstract'] for paper in papers]
    article_titles = [paper['article_title'] for paper in papers]

    # Compute embeddings for all papers
    corpus_embeddings = model.encode(article_texts, convert_to_tensor=True)
    umap_embeddings = UMAP(n_neighbors=5, n_components=2, metric='cosine', random_state=42)
    low_dim_embeddings = umap_embeddings.fit_transform(corpus_embeddings)

    # Create and save high dimensional article embeddings  according to your model
    # result = dict(zip(article_titles, corpus_embeddings))
    # with open('../embeddings/' + model_name + '_high_dim.json', 'w') as f:
    #     json.dump(result, f)
    # print("wrote to a file")

    # Create and save low dimensional article embeddings according to your model
    result = dict(zip(article_titles, low_dim_embeddings.tolist()))
    print(result)
    with open('../embeddings/low_dim/' + model_name + '_low_dim.json', 'x') as f:
        json.dump(result, f)
    print("wrote to a file")


def search_papers(title, abstract, model_name):
    with open('../articles_data/all_articles_with_thumbnail_metadata.json') as f:
        papers = json.load(f)

        # We then load the allenai-specter model with SentenceTransformers
    model = SentenceTransformer(model_name)
    model_name = model_name.replace('-', '_').lower()

    # To encode the papers, we must combine the title and the abstracts to a single string
    article_texts = [paper['article_title'] + '[SEP]' + paper['abstract'] for paper in papers]
    article_titles = [paper['article_title'] for paper in papers]

    # Compute embeddings for all papers
    corpus_embeddings = model.encode(article_texts, convert_to_tensor=True)
    query_embedding = model.encode(title + '[SEP]' + abstract, convert_to_tensor=True)

    search_hits = util.semantic_search(query_embedding, corpus_embeddings)
    search_hits = search_hits[0]  # Get the hits for the first query

    print("\n\nPaper:", title)
    print("Most similar papers:")
    for hit in search_hits:
        related_paper = papers[hit['corpus_id']]
        print("{:.2f}\t{}\t{}".format(hit['score'], related_paper['article_title'],
                                      related_paper['published_year']))



def create_bioword_vec_low_dim():
    import umap.umap_ as umap
    import json
    with open('../embeddings/high_dim/biowordvec_high_dim.json') as f:
        emb_wv = json.load(f)

    umap_embeddings = umap.UMAP(n_neighbors=5, n_components=2, metric='cosine', random_state=42)
    low_dim_embeddings = umap_embeddings.fit_transform(list(emb_wv.values()))
    low_dim_embeddings = low_dim_embeddings.tolist()
    result = dict(zip(emb_wv.keys(), low_dim_embeddings))
    print(result)
    with open('../embeddings/low_dim/biowordvec_low_dim.json', 'w') as f:
        json.dump(result, f)
    print("wrote to a file")


def load_data():
    with open('../articles_data/all_articles_with_thumbnail_metadata.json') as f:
        papers = json.load(f)

    # To encode the papers, we must combine the title and the abstracts to a single string
    article_texts = [paper['article_title'] + ' ' + paper['abstract'] for paper in
                     papers]
    article_titles = [paper['article_title'] for paper in papers]
    return article_titles, article_texts


def generate_bow():
    from sklearn.feature_extraction.text import CountVectorizer

    article_titles, article_texts = load_data()

    vectorizer = CountVectorizer(min_df=5, stop_words='english')
    word_doc_matrix = vectorizer.fit_transform(article_texts).todense()

    result = dict(zip(article_titles, word_doc_matrix.tolist()))
    with open('../embeddings/high_dim/bow_high_dim.json', 'w') as f:
        json.dump(result, f)
    print("wrote to a file")

    word_doc_matrix = vectorizer.fit_transform(article_texts)
    emb = umap.UMAP(n_components=2, metric='cosine').fit(word_doc_matrix)
    result = dict(zip(article_titles, emb.embedding_.tolist()))
    with open('../embeddings/low_dim/bow_low_dim.json', 'w') as f:
        json.dump(result, f)
    print("wrote to a file")


def generate_tfidf():
    article_titles, article_texts = load_data()
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf_vectorizer = TfidfVectorizer(min_df=5, stop_words='english')
    tfidf_word_doc_matrix = tfidf_vectorizer.fit_transform(article_texts).todense()

    result = dict(zip(article_titles, tfidf_word_doc_matrix.tolist()))
    with open('../embeddings/high_dim/tfidf_high_dim.json', 'w') as f:
        json.dump(result, f)
    print("wrote to a file")
    tfidf_word_doc_matrix = tfidf_vectorizer.fit_transform(article_texts)
    tfidf_embedding = umap.UMAP(n_components=2, metric='cosine').fit(tfidf_word_doc_matrix)
    result = dict(zip(article_titles, tfidf_embedding.embedding_.tolist()))
    with open('../embeddings/low_dim/tfidf_low_dim.json', 'w') as f:
        json.dump(result, f)
    print("wrote to a file")


if __name__ == "__main__":
    # create_high_and_low_dim_embeddings_for_models('all-MiniLM-L6-v2')
    # create_high_and_low_dim_embeddings_for_models('all-mpnet-base-v2')
    # create_high_and_low_dim_embeddings_for_models('allenai-specter')
    generate_tfidf()
    generate_bow()

    # This paper was the EMNLP 2019 Best Paper
    # search_papers(title='The Virtual Reality Flow Lens for Blood Flow Exploration',
    #               abstract='The exploration of time-dependent measured or simulated blood flow is challenging due to the complex three-dimensional structure of vessels and blood flow patterns. Especially on a 2D screen, understanding their full shape and interacting with them is difficult. Critical regions do not always stand out in the visualization and may easily be missed without proper interaction and filtering techniques. The FlowLens [GNBP11] was introduced as a focus-and-context technique to explore one specific blood flow parameter in the context of other parameters for the purpose of treatment planning. With the recent availability of affordable VR glasses it is possible to adapt the concepts of the FlowLens into immersive VR and make them available to a broader group of users. Translating the concept of the Flow Lens to VR leads to a number of design decisions not only based around what functions to include, but also how they can be made available to the user. In this paper, we present a configurable focus-and-context visualization for the use with virtual reality headsets and controllers that allows users to freely explore blood flow data within a VR environment. The advantage of such a solution is the improved perception of the complex spatial structures that results from being surrounded by them instead of observing through a small screen.',
    #               model_name="allenai-specter")
    # search_papers("Interactive Exploded Views for Molecular Structures",
    #               "We propose an approach to interactively create exploded views of molecular structures with the goal to help domain experts in their design process and provide them with a meaningful visual representation of component relationships. Exploded views are excellently suited to manage visual occlusion of structure components, which is one of the main challenges when visualizing complex 3D data. In this paper, we discuss four key parameters of an exploded view: explosion distance, direction, order, and the selection of explosion components. We propose two strategies, namely the structure-derived exploded view and the interactive free-form exploded view, for computing these four parameters systematically. The first strategy allows scientists to automatically create exploded views by computing the parameters from the given object structures. The second strategy further supports them to design and customize detailed explosion paths through user interaction. Our approach features the possibility to animate exploded views, to incorporate ease functions into these animations and to display the explosion path of components via arrows. Finally, we demonstrate three use cases with various challenges that we investigated in collaboration with a domain scientist. Our approach, therefore, provides interesting new ways of investigating and presenting the design layout and composition of complex molecular structures.",
    #               "allenai-specter")

import json

from sentence_transformers import SentenceTransformer
from umap import UMAP


def create_high_and_low_dim_embeddings_for_models(model_name):
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


# def search_papers(title, abstract):
#     query_embedding = model.encode(title + '[SEP]' + abstract, convert_to_tensor=True)
#
#     search_hits = util.semantic_search(query_embedding, corpus_embeddings)
#     search_hits = search_hits[0]  # Get the hits for the first query
#
#     print("\n\nPaper:", title)
#     print("Most similar papers:")
#     for hit in search_hits:
#         related_paper = papers[hit['corpus_id']]
#         print("{:.2f}\t{}\t{}".format(hit['score'], related_paper['article_title'],
#                                       related_paper['published_date']))
#
#
# # This paper was the EMNLP 2019 Best Paper
# search_papers(title='The Virtual Reality Flow Lens for Blood Flow Exploration',
#               abstract='The exploration of time-dependent measured or simulated blood flow is challenging due to the complex three-dimensional structure of vessels and blood flow patterns. Especially on a 2D screen, understanding their full shape and interacting with them is difficult. Critical regions do not always stand out in the visualization and may easily be missed without proper interaction and filtering techniques. The FlowLens [GNBP11] was introduced as a focus-and-context technique to explore one specific blood flow parameter in the context of other parameters for the purpose of treatment planning. With the recent availability of affordable VR glasses it is possible to adapt the concepts of the FlowLens into immersive VR and make them available to a broader group of users. Translating the concept of the Flow Lens to VR leads to a number of design decisions not only based around what functions to include, but also how they can be made available to the user. In this paper, we present a configurable focus-and-context visualization for the use with virtual reality headsets and controllers that allows users to freely explore blood flow data within a VR environment. The advantage of such a solution is the improved perception of the complex spatial structures that results from being surrounded by them instead of observing through a small screen.')

if __name__ == "__main__":
    # create_high_and_low_dim_embeddings_for_models('all-MiniLM-L6-v2')
    create_high_and_low_dim_embeddings_for_models('all-mpnet-base-v2')
    # create_high_and_low_dim_embeddings_for_models('allenai-specter')

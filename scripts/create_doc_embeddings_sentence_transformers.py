import json

import umap
from sentence_transformers import SentenceTransformer
from umap import UMAP


def high_low_dim_emb_for_sentence_tranformer_models(model_name):
    with open('../articles_data/all_articles_with_thumbnail_metadata.json') as f:
        papers = json.load(f)

    # We then load the allenai-specter model with SentenceTransformers
    model = SentenceTransformer(model_name)
    model_name = model_name.split('/')[-1].replace('-', '_').lower()

    # To encode the papers, we must combine the title and the abstracts to a single string
    article_texts = [paper['article_title'] + '[SEP]' + paper['abstract'] for paper in papers]
    article_titles = [paper['article_title'] for paper in papers]

    # Compute embeddings for all papers
    corpus_embeddings = model.encode(article_texts, convert_to_tensor=True)
    umap_embeddings = UMAP(n_neighbors=5, n_components=2, metric='cosine', random_state=42)
    low_dim_embeddings = umap_embeddings.fit_transform(corpus_embeddings)
    low_dim_embeddings = low_dim_embeddings.tolist()
    corpus_embeddings = corpus_embeddings.tolist()
    result_high = dict(zip(article_titles, corpus_embeddings))


    with open('../embeddings/high_dimension/' + model_name + '_high_dim.json', 'w') as f:
        json.dump(result_high, f)

    result_low = dict(zip(article_titles, low_dim_embeddings))
    with open('../embeddings/low_dimension/' + model_name + '_low_dim.json', 'w') as f:
        json.dump(result_low, f)

if __name__ == "__main__":
    high_low_dim_emb_for_sentence_tranformer_models('all-mpnet-base-v2')
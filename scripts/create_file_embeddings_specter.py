import json

from sentence_transformers import SentenceTransformer, util

with open('../articles_data/all_articles_with_thumbnail_metadata.json') as f:
    papers = json.load(f)

print(len(papers), "papers loaded")

# We then load the allenai-specter model with SentenceTransformers
model = SentenceTransformer('all-MiniLM-L6-v2')

# To encode the papers, we must combine the title and the abstracts to a single string
paper_texts = [paper['article_title'] + '[SEP]' + paper['abstract'] for paper in papers]
paper_titles = [paper['article_title'] for paper in papers]

# Compute embeddings for all papers
corpus_embeddings = model.encode(paper_texts, convert_to_tensor=True)


#
# # Create and save file according to your model
# result = dict(zip(paper_titles, corpus_embeddings))
# with open('../embeddings/specter_embeddings.json', 'w') as f:
#     json.dump(result, f)
# print("wrote to a file")

def search_papers(title, abstract):
    query_embedding = model.encode(title + '[SEP]' + abstract, convert_to_tensor=True)

    search_hits = util.semantic_search(query_embedding, corpus_embeddings)
    search_hits = search_hits[0]  # Get the hits for the first query

    print("\n\nPaper:", title)
    print("Most similar papers:")
    for hit in search_hits:
        related_paper = papers[hit['corpus_id']]
        print("{:.2f}\t{}\t{}".format(hit['score'], related_paper['article_title'],
                                      related_paper['published_date']))


# This paper was the EMNLP 2019 Best Paper
search_papers(title='The Virtual Reality Flow Lens for Blood Flow Exploration',
              abstract='The exploration of time-dependent measured or simulated blood flow is challenging due to the complex three-dimensional structure of vessels and blood flow patterns. Especially on a 2D screen, understanding their full shape and interacting with them is difficult. Critical regions do not always stand out in the visualization and may easily be missed without proper interaction and filtering techniques. The FlowLens [GNBP11] was introduced as a focus-and-context technique to explore one specific blood flow parameter in the context of other parameters for the purpose of treatment planning. With the recent availability of affordable VR glasses it is possible to adapt the concepts of the FlowLens into immersive VR and make them available to a broader group of users. Translating the concept of the Flow Lens to VR leads to a number of design decisions not only based around what functions to include, but also how they can be made available to the user. In this paper, we present a configurable focus-and-context visualization for the use with virtual reality headsets and controllers that allows users to freely explore blood flow data within a VR environment. The advantage of such a solution is the improved perception of the complex spatial structures that results from being surrounded by them instead of observing through a small screen.')

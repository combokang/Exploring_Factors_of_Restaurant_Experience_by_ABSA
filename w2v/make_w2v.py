import pandas as pd
from gensim.models import Word2Vec

# created by lemmatize_reviews_for_w2v.py
df = pd.read_csv("outputs/replace_lemma/reviews_lemma.csv")
processed_corpus = list(df["lemma_tokens"].apply(lambda x: str(x).split()))

# make model
# tokens appear under 3 will be removed
threshold = 3
model = Word2Vec(
    sentences=processed_corpus,
    vector_size=100,
    window=5,
    min_count=threshold,
    workers=4,
)
model.save("w2v/word2vec_no_twice.model")

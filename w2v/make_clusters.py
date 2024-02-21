import pandas as pd
from gensim.models import Word2Vec
from tqdm import tqdm


def make_clusters(
    unclustered_aspect: str, threshold: float, model: "Word2Vec", clusters: list
) -> None:
    """面向事先依照頻率排序
    如果一個面向與一組cluster中所有面向的相似度平均大於threshold，則加入該cluster
    若一個面向和多組cluster的平均相似度都大於threshold，則加入平均相似度最高者

    Aspects are pre-ordered by frequency.
    If the average cosine similarity between a cluster's every aspect and the current aspect is greater than the threshold, add the current aspect into the cluster.
    If there are multiple clusters that meet this condition, choose the one has the greatest similarity.
    """
    unclustered_aspect = str(unclustered_aspect).replace(" ", "_")
    if unclustered_aspect in model.wv:
        avg_similarities = []
        for cluster in clusters:
            cos_similarities = []
            for clustered_aspect in cluster:
                cos_similarities.append(
                    model.wv.similarity(unclustered_aspect, clustered_aspect)
                )
            avg = sum(cos_similarities) / len(cos_similarities)
            if avg > threshold:
                avg_similarities.append(avg)
            else:
                avg_similarities.append(0)
        if len(avg_similarities) == 0:
            clusters.append([unclustered_aspect])
        else:
            mx_avg = max(avg_similarities)
            if mx_avg != 0:
                i = avg_similarities.index(mx_avg)
                clusters[i].append(unclustered_aspect)
            else:  # cannot fit in any existing cluster
                clusters.append([unclustered_aspect])


model = Word2Vec.load("w2v/word2vec_no_twice.model")
tqdm.pandas()

df = pd.read_csv("outputs/senti_count.csv", encoding="utf-8")

# 0.33 has the best result
threshold = 0.33

clusters = []

df["Term"].progress_apply(
    make_clusters,
    args=(
        threshold,
        model,
        clusters,
    ),
)

print("cosine similarity threshold: ", threshold)
print("amount of clusters: ", len(clusters))

with open(
    f"w2v/no_twice/clusters_thr{threshold}_clu{len(clusters)}.txt",
    "w",
    encoding="utf-8",
) as f:
    for line in clusters:
        line = ",".join(line)
        print(line, file=f)

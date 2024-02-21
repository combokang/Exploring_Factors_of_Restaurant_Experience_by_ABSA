import matplotlib.pyplot as plt
import pandas as pd
import PIL.Image as Image
from wordcloud import WordCloud

Image.MAX_IMAGE_PIXELS = 160000000


def get_wordcloud(r_type=""):
    if r_type != "":
        r_type = rf"{r_type}/"

    plt.figure(figsize=(10, 5))

    # create WordCloud object and assign arguments
    # Insufficient width/height may result in insufficient space to display small-weight terms.
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        scale=14,
        prefer_horizontal=1,
        min_font_size=10,
    )

    cluster_count = df["Cluster"].nunique()
    for i in range(cluster_count):

        cluster_fliter = i

        subdf = df[df["Cluster"] == cluster_fliter]

        # 建立單詞與權重的字典
        # create term-weight dictionary
        word_weights = subdf[["Term", "TOTAL"]]
        word_weights = word_weights.set_index("Term").to_dict()["TOTAL"]

        # 生成文字雲
        # create wordcloud
        wordcloud.generate_from_frequencies(word_weights)

        # 顯示生成的文字雲
        # show wordcloud
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(rf"outputs/wordclouds/{r_type}{cluster_fliter}.png", dpi=300)
        plt.clf()


# For all resaurant
df = pd.read_csv("outputs/term_count_with_cluster.csv", index_col=[0])
get_wordcloud()

# For different resaurant types
# r_types = [
#             "italian",
#             "chinese",
#             "american"
#            ]
# for r_type in r_types:
#     df = pd.read_csv(f"outputs/types/{r_type}_term_count_with_cluster.csv", index_col = [0])
#     get_wordcloud(r_type)

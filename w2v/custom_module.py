import string

import pandas as pd
from nltk.corpus import wordnet


def handle_csv_error(path):
    df = pd.read_csv(path, header=None, sep=",", names=list(range(13)))
    df.to_csv(f"{path}_error", sep=",", header=None)


def reset_csv_index_by_reviewno(path):
    # reset index by ["restaurant_id","review_no_per_rest"]
    df = pd.read_csv(
        path, encoding="utf-8", index_col=0  # "dataset_split/predicting_full.csv"
    )
    df.sort_values(by=["restaurant_id", "review_no_per_rest"], inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.to_csv(path.replace(".csv", "_new.csv"), encoding="utf-8", index_label="id")


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    elif treebank_tag.startswith("V"):
        return wordnet.VERB
    elif treebank_tag.startswith("R"):
        return wordnet.ADV
    else:  # default noun
        return wordnet.NOUN


def seperate_by_punc(s: string):
    ss = s.split()
    for i, w in enumerate(ss):
        wl = list(w)
        for j, t in enumerate(wl[:-1]):
            if t in PUNCTUATION or wl[j + 1] in PUNCTUATION:
                wl[j] = t + " "
        ss[i] = "".join(wl)
    return " ".join(ss)


Chinese_punctuation = "＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､　、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。"
PUNCTUATION = string.punctuation + Chinese_punctuation

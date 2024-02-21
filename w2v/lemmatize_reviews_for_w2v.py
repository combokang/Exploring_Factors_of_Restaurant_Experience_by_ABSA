import re
import string

import emoji
import nltk
import pandas as pd
from custom_module import get_wordnet_pos, seperate_by_punc
from gensim.parsing.preprocessing import (
    STOPWORDS,
    preprocess_string,
    remove_stopwords,
    strip_multiple_whitespaces,
    strip_numeric,
)
from nltk.stem import WordNetLemmatizer
from tqdm.auto import tqdm


def my_lemmatize(tokens: list) -> list:
    """lemmatize"""
    token_tag_pair = nltk.pos_tag(tokens)
    lemma_tokens = [
        wnl.lemmatize(pair[0].lower(), get_wordnet_pos(pair[1]))
        for pair in token_tag_pair
    ]
    return lemma_tokens


def my_strip_punctuation(s: str) -> str:
    """strip punctuation"""
    ss = list(s)
    for i, t in enumerate(ss):
        if t in MY_PUNCTUATION:
            last_token = ss[i - 1] if i > 0 else None
            next_token = ss[i + 1] if i < len(ss) - 1 else None
            if last_token != "_" and next_token != "_":
                ss[i] = " "
    return "".join(ss)


def lemma_and_replace_phrase(s: str, lemma_aspects: list):
    """lemmatize corpus and replace phrased aspect"""
    flter = [
        lambda x: x.lower(),
        lambda x: emoji.replace_emoji(x, replace=""),
        seperate_by_punc,
    ]

    tokens = preprocess_string(s, flter)
    text = " ".join(my_lemmatize(tokens))

    # replace phrased aspect with phrased_aspect
    for aspect in lemma_aspects:
        if re.search(rf"\b{aspect}\b", text):
            sub_aspect = aspect.replace(" ", "_")
            text = re.sub(rf"\b{aspect}\b", sub_aspect, text)

    flter = [
        my_strip_punctuation,
        strip_numeric,
        lambda x: remove_stopwords(x, MY_STOPWORD),
        strip_multiple_whitespaces,
    ]
    text = " ".join(preprocess_string(text, flter))
    return text


tqdm.pandas()
wnl = WordNetLemmatizer()


Chinese_punctuation = "＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､　、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。"
MY_PUNCTUATION = (string.punctuation + Chinese_punctuation).replace("_", "")

# customized stopword
MY_STOPWORD = STOPWORDS.union({"t", "s", "day"}).difference({"bill"})


reviews_pcd_df = pd.read_csv("text_data/reviews_processed.csv")

# created by senti_count.py
with open("outputs/replace_lemma/lemma_phrase_tokens.txt", "r", encoding="utf-8") as f:
    lemma_aspects = f.read().splitlines()

# turn phrased aspects into a signal token
reviews_pcd_df["lemma_tokens"] = reviews_pcd_df["review_body"].progress_apply(
    lemma_and_replace_phrase, args=(lemma_aspects,)
)

# create lemmatized corpus
reviews_pcd_df.to_csv(
    "outputs/replace_lemma/reviews_lemma.csv", encoding="utf-8", index=None
)

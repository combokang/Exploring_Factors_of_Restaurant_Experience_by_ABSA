import re
import string

import emoji
import pandas as pd
from pandas import Series


def isenglish(row: "Series") -> bool:
    """check if the review is english"""
    new_string = str(row).translate(str.maketrans("", "", PUNCTUATION))
    has_alphabet = bool(re.search("[a-zA-Z]", new_string))
    return new_string.isascii() and has_alphabet


Chinese_punctuation = "＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､　、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。"
PUNCTUATION = string.punctuation + Chinese_punctuation

reviews_df = pd.read_csv(
    "text_data/reviews.csv", encoding="utf-8", on_bad_lines="warn", low_memory=False
)

# 去除換行
# replace every line break with space
reviews_df["review_body"] = reviews_df["review_body"].apply(
    lambda x: str(x).replace("\n", " ").replace("\r", " ")
)

# 去除emoji
# remove emoji
reviews_df["review_body"] = reviews_df["review_body"].apply(emoji.replace_emoji)

# 除去1個單字以下的評論
# remove reviews under 2 tokens
flter1 = reviews_df["review_body"].apply(
    lambda x: True if len(str(x).split(" ")) > 1 else False
)

# 去除非英文字母、標點組合的評論、無英文字母的評論
# review reviews that are non-english or no alphabets
flter2 = reviews_df["review_body"].apply(isenglish)

reviews_df_not_empty = reviews_df[flter1 & flter2]
reviews_df_not_empty.reset_index(drop=True, inplace=True)

# save file
reviews_df_not_empty.to_csv(
    "text_data/reviews_processed.csv", encoding="utf-8", index_label="id"
)  # 63878

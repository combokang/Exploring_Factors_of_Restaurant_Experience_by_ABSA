import nltk
import pandas as pd
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm


def get_wordnet_pos(treebank_tag: str) -> str:
    """convert part-of-speech tags"""
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    elif treebank_tag.startswith("V"):
        return wordnet.VERB
    elif treebank_tag.startswith("R"):
        return wordnet.ADV
    else:  # default noun
        return wordnet.NOUN


def ABSA_lemmatizer(tokens: list, positions: list) -> list:
    """lemmatize"""
    # get part-of-speech tags
    token_tag_pair = nltk.pos_tag(tokens)

    # lemmatized aspects of a sentence
    processed_aspects = []

    # lemmatization
    for position in positions:
        # lemmatized tokens of an aspect
        lemma_aspect_tokens = []
        for i in position:
            lemma_aspect_tokens.append(
                wnl.lemmatize(
                    token_tag_pair[i - 1][0].lower(),
                    get_wordnet_pos(token_tag_pair[i - 1][1]),
                )
            )
        lemma_aspect = " ".join(lemma_aspect_tokens)
        processed_aspects.append(lemma_aspect)
    return processed_aspects


def count_sentiment(
    sentis: list, tokens: list, positions: list, senti_count: dict
) -> None:
    """count sentiment frequency of each aspect term"""
    processed_aspects = ABSA_lemmatizer(tokens, positions)

    # count sentiment freqency of every aspect
    for term, senti in zip(processed_aspects, sentis):
        if term not in senti_count["Term"]:
            senti_count["Term"].append(term)
            senti_count["POS"].append(0)
            senti_count["NEG"].append(0)
            senti_count["NEU"].append(0)
            senti_count["TOTAL"].append(0)
        term_index = senti_count["Term"].index(term)
        senti_count["TOTAL"][term_index] += 1
        if senti == "Positive":
            senti_count["POS"][term_index] += 1
        elif senti == "Negative":
            senti_count["NEG"][term_index] += 1
        else:  # Neutral
            senti_count["NEU"][term_index] += 1


def create_senti_count(r_type: str) -> None:
    # read ABSA predicting result
    if r_type == "":
        atepc_df = pd.read_json(
            "outputs/ATEPC_results/result.ALL.json", encoding="UTF-8"
        )
    else:
        atepc_df = pd.read_json(
            f"outputs/ATEPC_results/result.{r_type}.json", encoding="UTF-8"
        )

    senti_count = {"Term": [], "POS": [], "NEG": [], "NEU": [], "TOTAL": []}

    atepc_df.progress_apply(
        lambda row: count_sentiment(
            row["sentiment"], row["tokens"], row["position"], senti_count
        ),
        axis=1,
    )

    flterd_df = pd.DataFrame(senti_count)

    if r_type == "":
        # remove term that barely appears
        total_threshold = 2
        flterd_df = flterd_df[(flterd_df["TOTAL"] > total_threshold)]

        flterd_df = flterd_df.sort_values(
            ["TOTAL", "POS", "NEG", "NEU"], ascending=False
        ).reset_index(drop=True)

        # 保存面向字詞情緒頻率
        # save aspect term sentiment freqeuncy
        flterd_df.to_csv("outputs/term_senti_count.csv", index_label="ID")

        # save lemmatized pharsed aspects
        lemma_phrased_aspects = flterd_df["Term"][
            flterd_df["Term"].apply(lambda x: " " in x)
        ]
        lemma_phrased_aspects.to_csv(
            "outputs/replace_lemma/lemma_phrase_tokens.txt", index=None, header=None
        )
    else:
        flterd_df = flterd_df.sort_values(
            ["TOTAL", "POS", "NEG", "NEU"], ascending=False
        ).reset_index(drop=True)

        # 保存面向字詞情緒頻率
        # save aspect term sentiment freqeuncy
        flterd_df.to_csv(
            f"text_data/types/{r_type}_term_senti_count.csv", index_label="ID"
        )


tqdm.pandas()
wnl = WordNetLemmatizer()

# For all resaurant types
r_type = ""

# For different resaurant types
# r_type = "italian"
# r_type = "chinese"
# r_type = "american"


create_senti_count(r_type)

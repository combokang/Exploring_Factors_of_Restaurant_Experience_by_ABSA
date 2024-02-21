import pandas as pd

df = pd.read_csv("text_data/reviews_processed.csv", index_col=[0])

# save samples for annotation
pre_annotated = df.sample(n=4000, random_state=0, axis=0)
pre_annotated = pre_annotated["review_body"]
pre_annotated.to_csv(
    "dataset_split/pre_annotated.csv", header=None, index=None, encoding="utf-8"
)

# save samples for predicting (with full information)
predicting_full = df[~df.index.isin(pre_annotated.index)]
predicting_full.reset_index(inplace=True, drop=True)
predicting_full.to_csv(
    "dataset_split/predicting_full.csv", encoding="utf-8", index_label="id"
)

# save predicting dataset (only review text)
predicting = predicting_full["review_body"]
predicting.to_csv(
    "dataset_split/predicting.csv", header=None, index=None, encoding="utf-8"
)

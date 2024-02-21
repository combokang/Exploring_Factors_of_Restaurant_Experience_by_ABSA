import pandas as pd
from pyabsa import AspectTermExtraction as ATEPC

# read predicting dataset
reviews_df = pd.read_csv("text_data/dataset_split/predicting_full.csv", index_col=0)
atepc_examples = reviews_df["review_body"].tolist()

# load checkpoint in 'checkpoints' folder
aspect_extractor = ATEPC.AspectExtractor(
    checkpoint="fast_lcf_atepc_custom_dataset_fusion_apcacc_90.15_apcf1_79.29_atef1_82.32",
    auto_device=True,  # False means load model on CPU
    cal_perplexity=True,
)

# predicting
aspect_extractor.predict(
    text=atepc_examples,
    save_result=True,
    # save_result=False,
    print_result=True,
    pred_sentiment=True,
)

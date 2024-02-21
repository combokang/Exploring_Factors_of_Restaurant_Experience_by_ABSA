import pandas as pd
from pandas import Series


def find_cluster(row: "Series", clusters: list) -> "Series":
    """find cluster that the term belongs"""
    aspect = str(row["Term"]).replace(" ", "_")
    for i, c in enumerate(clusters):
        if str(aspect) in c:
            row["Cluster"] = i + 1
            row["Cluster_1Word"] = c[0]
    return row


def assign_cluster(r_type: str = "") -> None:
    # if for different restaurant types than adjust path name
    if r_type != "":
        r_type = rf"types/{r_type}_"

    df = pd.read_csv(rf"outputs/{r_type}term_senti_count.csv", encoding="utf-8")
    df = df.apply(find_cluster, args=(clusters,), axis=1)
    df[["ID", "Term", "TOTAL", "Cluster", "Cluster_1Word"]].to_csv(
        rf"outputs\{r_type}term_count_with_cluster.csv", encoding="utf-8", index=None
    )

    group_by = (
        df.groupby(["Cluster_1Word"], as_index=False)
        .sum()
        .sort_values(["TOTAL", "POS", "NEG", "NEU"], ascending=False)
        .reset_index(drop=True)
    )
    group_by = group_by.drop("ID", axis=1).drop("Cluster", axis=1)
    group_by.to_csv(
        rf"outputs/{r_type}cluster_senti_count.csv",
        encoding="utf-8",
        index_label="Index",
    )


# read cluster imformation
result_path = "w2v/no_twice/clusters_thr0.33_clu25.txt"

with open(result_path, "r", encoding="utf-8") as f:
    clusters = f.read().splitlines()
    clusters = [i.split(",") for i in clusters]

# For all resaurant types
# r_type = ""

# For different resaurant types
r_type = "italian"
# r_type = "chinese"
# r_type = "american"

assign_cluster(r_type)

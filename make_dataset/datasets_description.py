dss = ["total", "train", "valid", "test"]
for ds in dss:
    if ds == "total":
        path = "text_data/dataset_split/annotated_easy.csv.apc"
    else:
        path = f"integrated_datasets/apc_datasets/105.Google_Maps_easy/googlemaps_easy.{ds}.dat.apc"
    with open(
        path,
        mode="r",
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
        dic = {"Positive": 0, "Negative": 0, "Neutral": 0}
        for i, line in enumerate(lines[2::3]):
            if line.strip() not in dic.keys():
                print(line)
                print(3 + i * 3)
                break
            else:
                dic[line.strip()] += 1
        print(f"{ds} set", "aspects amount:", int(len(lines) / 3), dic)

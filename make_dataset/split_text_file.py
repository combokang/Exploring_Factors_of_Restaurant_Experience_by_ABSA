from collections import namedtuple


def split_text_file(from_path, to_path, slice_from=None, slice_to=None):
    with open(from_path, mode="r", encoding="utf-8") as f:
        lines = f.readlines()[slice_from:slice_to]
        # lines = f.readlines()[5361:7371]
    with open(to_path, mode="w", encoding="utf-8") as f:
        f.writelines(lines)


Dataset = namedtuple("Dataset", ["name", "slice_from", "slice_to"])
train = Dataset("train", None, 5361)
valid = Dataset("valid", 5361, 7371)
test = Dataset("test", 7371, None)


lst = [train, valid, test]

path1 = "text_data/dataset_split/annotated_easy.csv.apc"
for i in lst:
    path2 = f"integrated_datasets/apc_datasets/105.Google_Maps_easy/googlemaps_easy.{i.name}.dat.apc"
    split_text_file(path1, path2, i.slice_from, i.slice_to)

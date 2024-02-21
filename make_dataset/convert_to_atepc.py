from pyabsa.utils.absa_utils.absa_utils import convert_apc_set_to_atepc_set

labels = ["train", "valid", "test"]

for i in labels:
    convert_apc_set_to_atepc_set(
        f"integrated_datasets/apc_datasets/105.Google_Maps/googlemaps_easy.{i}.dat.apc"
    )  # for custom datasets, absolute path is recommended for this function

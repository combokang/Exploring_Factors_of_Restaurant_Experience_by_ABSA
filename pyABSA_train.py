import warnings

from pyabsa import AspectTermExtraction as ATEPC
from pyabsa import DeviceTypeOption, ModelSaveOption

# load model
config = (
    ATEPC.ATEPCConfigManager.get_atepc_config_english()
)  # this config contains 'pretrained_bert', it is based on pretrained models
config.model = ATEPC.ATEPCModelList.FAST_LCF_ATEPC  # improved version of LCF-ATEPC

# load dataset in 'integrated_datasets'
dataset = "105.Google_Maps_easy"

warnings.filterwarnings("ignore")

# set hyperparameters
config.SRD = 4
config.lcf = "cdm"
config.max_seq_len = 512
config.batch_size = 8
config.patience = 2
config.log_step = -1
config.seed = [1]
config.verbose = False
# If verbose == True, PyABSA will output the model strcture and seversal processed data examples
config.notice = (
    "This is an training example for aspect term extraction"  # for memos usage
)

# load trainer
trainer = ATEPC.ATEPCTrainer(
    config=config,
    dataset=dataset,
    # from_checkpoint="english"
    auto_device=DeviceTypeOption.AUTO,  # use cuda if available
    checkpoint_save_mode=ModelSaveOption.SAVE_MODEL_STATE_DICT,
    load_aug=False,
)

# aspect_extractor = trainer.load_trained_model()

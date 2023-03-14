import os

from trainer import Trainer, TrainerArgs

from TTS.config import load_config
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.tts.configs.vits_config import VitsConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.vits import Vits, VitsAudioConfig
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.utils.audio import AudioProcessor
import argparse

OUTPUT_PATH = "output/"
CONFIG_FILE_NAME = "config.json"
DEFAULT_MODEL_NAME = "new_model"
DATASETS_DIR = "audiofiles/datasets"


def validate_input(args):
    assert isinstance(args.gpu_num, int)
    assert args.gpu_num > 0
    assert args.language in ('en', 'pl')
    if args.model_path:
        assert args.model_path.endswith('.pth')
        assert os.path.exists(os.path.join(OUTPUT_PATH, args.model_path))
        assert CONFIG_FILE_NAME in os.listdir(os.path.join(OUTPUT_PATH, args.model_path))
    assert os.path.exists(os.path.join(DATASETS_DIR, args.dataset_name))


def train(model_path, dataset_name, language):

    run_name = model_path.split('/')[-2] if model_path else DEFAULT_MODEL_NAME
    mode = 'continue' if model_path else 'new'

    dataset_config = BaseDatasetConfig(
        formatter="ljspeech", meta_file_train="metadata.csv", path=os.path.join(DATASETS_DIR, dataset_name))

    audio_config = VitsAudioConfig(
        sample_rate=22050, win_length=1024, hop_length=256, num_mels=80, mel_fmin=0, mel_fmax=None
    )

    print(f"Mode=={mode}\n")

    if mode == 'new':
        config = VitsConfig(
            audio=audio_config,
            run_name=run_name,
            batch_size=20,
            eval_batch_size=20,
            batch_group_size=4,
            # num_loader_workers=8,
            num_loader_workers=4,
            num_eval_loader_workers=4,
            run_eval=True,
            test_delay_epochs=-1,
            epochs=100000,
            save_step=10000,
            save_checkpoints=True,
            save_n_checkpoints=10,
            save_best_after=1000,
            # text_cleaner="english_cleaners",
            text_cleaner="multilingual_cleaners",
            eval_split_size=0.1,
            use_phonemes=True,
            phoneme_language=language,
            phoneme_cache_path=os.path.join(OUTPUT_PATH, "phoneme_cache"),
            compute_input_seq_cache=True,
            print_step=10,
            print_eval=True,
            mixed_precision=True,
            output_path=OUTPUT_PATH,
            datasets=[dataset_config],
            cudnn_benchmark=False,
        )
    else:
        config = load_config(os.path.join(OUTPUT_PATH, os.path.join(OUTPUT_PATH, model_path), CONFIG_FILE_NAME))

    #print(config)
    # INITIALIZE THE AUDIO PROCESSOR
    # Audio processor is used for feature extraction and audio I/O.
    # It mainly serves to the dataloader and the training loggers.
    ap = AudioProcessor.init_from_config(config)

    # INITIALIZE THE TOKENIZER
    # Tokenizer is used to convert text to sequences of token IDs.
    # config is updated with the default characters if not defined in the config.
    tokenizer, config = TTSTokenizer.init_from_config(config)

    # LOAD DATA SAMPLES
    # Each sample is a list of [text, audio_file_path, speaker_name]
    # You can define your custom sample loader returning the list of samples.
    # Or define your custom formatter and pass it to the load_tts_samples.
    # Check TTS.tts.datasets.load_tts_samples for more details.
    train_samples, eval_samples = load_tts_samples(
        dataset_config,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    model = Vits(config, ap, tokenizer, speaker_manager=None)
    if mode == 'continue':
        model.load_checkpoint(config, os.path.join(OUTPUT_PATH, model_path))

    # init the trainer and begin
    trainer = Trainer(
        TrainerArgs(),
        config,
        OUTPUT_PATH,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    trainer.fit()


if __name__=='__main__':

    parser = argparse.ArgumentParser(prog='Train',
                                     description='Trains model from scratch or continues training of given model')
    parser.add_argument('-m', '--model_path', action='store', dest='model_path', default=None,
                        help='Model path (from output/), starts from scratch if not given.'
                             ' There must be config.json next to model!')
    parser.add_argument('-l', '--language', action='store', dest='language', default='en',
                        help='Language of model (en/pl). Default: en.')
    parser.add_argument('-d', '--dataset', action='store', dest='dataset_name', default='dataset',
                        help=f'Dataset name (from {DATASETS_DIR}). Default: dataset.')
    parser.add_argument('-g', '--gpu', action='store', dest='gpu_num', required=True, help='GPU number.')

    args = parser.parse_args()
    validate_input(args)

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_num

    train(args.model_path, args.dataset_name, args.language)
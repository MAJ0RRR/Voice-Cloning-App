import os
import wave
from pydub import AudioSegment
from distutils.dir_util import copy_tree
import glob

from splits_equal import split_equal
from splits_silence import split_silence
from noise import remove_noise
from whispertrans import create_transcription
from discard_transcriptions import discard_transcriptions
from train_experimental import train


def trim_wavs(source, destinantion, desired_len_ms):
    len_sum = 0
    audiofiles_src = glob.glob(source + "/*")
    for idx, audiofile in enumerate(audiofiles_src):
        ext = os.path.splitext(audiofile)[1]
        if ext == ".wav":
            audio_segment = AudioSegment.from_wav(audiofile)
        elif ext == ".mp3":
            audio_segment = AudioSegment.from_mp3(audiofile)
        else:
            print(f'UNSUPPORTED EXTENSION:{ext}, {audiofile}')
        len_sum += len(audio_segment)
        if len_sum > desired_len_ms:
            trimmed_len = len_sum - desired_len_ms
            trimmed_audio_segment = audio_segment[:-trimmed_len]
        else:
            trimmed_audio_segment = audio_segment
        # Export the trimmed audio segment as a wav file
        dest_file = os.path.join(destinantion, str(idx) + ext)
        trimmed_audio_segment.export(dest_file, format=ext[1:])
        if len_sum >= desired_len_ms:
            break


def run_pipeline(gpu_num, experiment_dir, raw_source, trim_source_length=0, silence_split_type="equal", split_len=8,
                 split_min_silence_lens=None, split_silence_threshs=None, remove_noises=True, dataset_name="dataset",
                 whisper_vram=10, discard_transcripts=True, discard_word_count=3, language="en",
                 model_path=None, run_name="experiment"):
    if split_silence_threshs is None:
        split_silence_threshs = [-45]
    if split_min_silence_lens is None:
        split_min_silence_lens = [300]

    splits_dir = os.path.join(experiment_dir, 'splits')
    datasets_dir = os.path.join(experiment_dir, 'datasets')
    dataset_dir = os.path.join(datasets_dir, dataset_name)
    if not os.path.exists(splits_dir):
        os.makedirs(splits_dir)
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    if trim_source_length == 0:
        audio_source = raw_source
    else:
        audio_source = os.path.join(experiment_dir, 'trimmed')
        trim_wavs(raw_source, audio_source, trim_source_length)

    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_num
    if silence_split_type == "equal":
        split_equal(splits_dir, audio_source, length=split_len)
    else:
        split_silence(splits_dir, audio_source, split_silence_threshs, split_min_silence_lens)

    if remove_noises:
        remove_noise(splits_dir, dataset_dir)
    else:
        copy_tree(splits_dir, dataset_dir)

    create_transcription(dataset_dir, language, whisper_vram)

    if discard_transcripts:
        discard_transcriptions(language, dataset_dir, discard_word_count)
    train(model_path, dataset_dir, language, run_name)


if __name__ == "__main__":
    run_pipeline(gpu_num="2", experiment_dir="experiment1", raw_source="audiofiles/raw")
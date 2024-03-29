import os
from pathlib import Path

WORKING_DIR = Path(os.getcwd())

# dir for basic voice models
MODEL_DIR_BASIC = os.path.join(WORKING_DIR, 'older-models/default')

# dir for generated voice models
MODEL_DIR_GENERATED = os.path.join(WORKING_DIR, 'older-models/generated')

# dirs for synthesized audio
GENERATED_DIR = os.path.join(WORKING_DIR, 'audiofiles/generated')
GENERATED_TEMP_DIR = os.path.join(WORKING_DIR, 'audiofiles/generated_temp')

# dir to put raw audio to generate samples
RAW_AUDIO_DIR = os.path.join(WORKING_DIR, 'audiofiles/raw')

# path to db_file
db_file = os.path.join(WORKING_DIR, 'app/db_file.db')

# path to output dir
OUTPUT_DIR = os.path.join(WORKING_DIR, "output")

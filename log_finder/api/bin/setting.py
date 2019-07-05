import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PREFIX_FILE = "dcauth.log-"
SUFFIX_COMPRESS = ".gz"

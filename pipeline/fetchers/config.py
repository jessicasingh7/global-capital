import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

EXA_API_KEY = os.getenv('EXA_API_KEY')
DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'data'
STATIC_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'static' / 'data'

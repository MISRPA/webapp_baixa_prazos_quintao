import os
from pathlib import Path
from enum import Enum


PATH_DIRETORIO = os.path.realpath(os.path.dirname(__file__))

WORK_DIR = Path(PATH_DIRETORIO)

MAIN_DIR = WORK_DIR.parent

class Directory(Enum):
    
    INPUT = os.path.join(MAIN_DIR,'input')
    OUTPUT = os.path.join(MAIN_DIR,'output')
    OUTPUT_APP = os.path.join(MAIN_DIR,'output_app')

    AWS = os.path.join(MAIN_DIR,'aws')
    AWS_DOWNLOADS = os.path.join(AWS,'downloads')
    
    LOG = os.path.join(MAIN_DIR,'log')
    
    TEMPLATES = os.path.join(MAIN_DIR,'templates')
    EMAIL_TEMPLATES = os.path.join(TEMPLATES,'email')
    
    BROWSER = os.path.join(MAIN_DIR,'browser')
    EXTENSIONS = os.path.join(BROWSER,'extensions')
    DOWNLOAD = os.path.join(BROWSER,'downloads')
    TEMP = os.path.join(BROWSER,'temp')
    ERRORS = os.path.join(BROWSER,'errors')


for dir in Directory:
    if not os.path.exists(dir.value):
        os.mkdir(dir.value)

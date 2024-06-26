import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
import os
import shutil

from module.directory import Directory, WORK_DIR
from module import settings 


class CustomFormatter(logging.Formatter):
    '''Classe para customizar o Logger'''

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] [%(name)s] [%(module)s.%(funcName)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        """_summary_

        Args:
            record (_type_): _description_

        Returns:
            _type_: _description_
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def task_log_cleanup(days=30):
    '''Faz a limpeza dos logs'''
    logger.info(f'TASK LOG CLEANUP')
    for folder in os.listdir(Directory.LOG.value):
        try:
            data_backup = datetime.strptime(folder,"%Y%m%d")
            if data_backup.date() <= (datetime.now() - timedelta(days=5)).date():
                shutil.rmtree(os.path.join(Directory.LOG.value, folder))
        except: 
            pass


logger = logging.getLogger(f"{settings.PID}")

data_str = datetime.now().strftime('%Y%m%d')
hora_str = datetime.now().strftime('%H%M%S')
folder = os.path.join(Directory.LOG.value,data_str)

if not os.path.exists(folder):
    os.mkdir(folder)

log_filename = os.path.join(folder, 'logfile.log')
file_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=0)

console_handler = logging.StreamHandler()

console_handler.setLevel(settings.LOG_LEVEL)
file_handler.setLevel(settings.LOG_LEVEL)
logger.setLevel(settings.LOG_LEVEL)

console_handler.setFormatter(CustomFormatter())
file_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(console_handler)
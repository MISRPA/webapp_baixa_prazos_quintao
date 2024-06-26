from datetime import datetime
import boto3
import zipfile
import rarfile
import re
import os

from .customlogger import logger
from ..directory import Directory
from .utils import random_generator, remove_espaco, remove_especiais


class BotoS3:

    def __init__(self,folder_name: str='',bucket: str='netview-tw',download_folder: str=Directory.AWS_DOWNLOADS.value) -> None:
        
        self.uploaded_files = {}
        
        self.bucket_name = bucket
        
        self._s3 = boto3.resource('s3')
        self._bucket = self._s3.Bucket(self.bucket_name)
        self._download_folder = download_folder

        self._folder_name = str(folder_name)

        self.folder = os.path.join(self._download_folder,self._folder_name)

    def _unzip_file(self,file) -> None:
        """Funcao generica para extrair arquivos compactados

        Args:
            file (_type_): _description_
        """       
        
        caminho_arquivo = os.path.join(self.folder,file)
        if file.endswith('.zip'):
            try: 
                with zipfile.ZipFile(os.path.join(self.folder,file),"r") as zip_ref:
                    zip_ref.extractall(self.folder)
                logger.info(f'Unziped file: {caminho_arquivo}')
            except Exception as e: 
                logger.warning(e)
                raise e
        elif file.endswith('.rar'):
            try: 
                with rarfile.RarFile(os.path.join(self.folder,file),"r") as rar_ref:
                    rar_ref.extractall(self.folder)
                logger.info(f'Unrared file: {caminho_arquivo}')
            except Exception as e: 
                logger.warning(e)
                raise e
        try: os.remove(caminho_arquivo)
        except Exception as ee: logger.warning(ee)

    def download_file(self,file_name: str,file_name_arq: str='') -> None:
        """Download do arquivo do Bucket

        Args:
            file_name (str): _description_

        Raises:
            e: _description_
        """  
        
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        
        if not file_name_arq: file_name_arq = file_name   

        try:
            self._bucket.download_file(file_name,os.path.join(self.folder,file_name_arq))
            logger.info(f'{file_name} downloaded to {os.path.join(self.folder,file_name_arq)}')
            while True:
                for file in os.listdir(self.folder):
                    if (
                        file.endswith('.zip') or file.endswith('.rar')
                        ):
                        self._unzip_file(file)
                        break
                else: break

            #TODO: Verificar limite caracteres upload arquivos
            #TODO remove os espacos e caracteres especiais
            # for file in listdir(self.folder):
            #     new_name = remove_espaco.sub('',file)
            #     new_name = remove_especiais.sub('',new_name)
            #     rename(path.join(self.folder,file),path.join(self.folder,new_name))
            
        except Exception as e: 
            logger.error(f'Cannot download {file_name} ::: {e}')
            raise e

    def upload_file(self,file_name: str,key='') -> str:
        """Upload do arquivo no Bucket

        Args:
            file_name (str): _description_

        Raises:
            e: _description_

        Returns:
            str: _description_
        """     
        try:
            object_data = open(file_name, 'rb')
            key = f'{random_generator()}_{key}_{datetime.today().strftime("%Y%m%d_%H%M%S_%f")}.{file_name.split(".")[-1]}'
            self._bucket.put_object(Key=key,Body=object_data)
            url_upload_file = f'https://{self.bucket_name}.s3.amazonaws.com/{key}'
            logger.info(f'{file_name} uploaded to {url_upload_file}')
            self.uploaded_files[url_upload_file] = key
        except Exception as e: 
            logger.error(f'Cannot upload {file_name} ::: {e}')
            raise e
        else: return url_upload_file,key


if __name__ == '__main__':
    from time import sleep
    s3 = BotoS3('netview-tw')
    # url_upload,key = s3.upload_file(r'E:\Ferreira-chagas\repositorios_git\robo_terceirizacao_cef\.gitignore')
    # sleep(10)
    s3.download_file('37635310_TW_05062023_172321.pdf')
    # s3.download_file('37042563_TW_16032023_094658.zip')
    # s3.download_file(s3.uploaded_files[url_upload])


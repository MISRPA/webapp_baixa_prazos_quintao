from unidecode import unidecode
import pandas as pd
import os
import openpyxl
import xlsxwriter

from .customlogger import logger

class Excel:
    '''Classe com metodos para trabalhar com o Excel'''
    def __init__(self,file_name: str,directory: str = ''):
        """_summary_

        Args:
            file_name (str): _description_
            directory (str, optional): _description_. Defaults to ''.
        """
        self.file_name = file_name
        self.directory = directory
        if not directory: self.path = file_name
        else: self.path = os.path.join(directory,file_name)
        self.writer = pd.ExcelWriter(self.path)

    @staticmethod
    def tratar_colunas(colunas: list) -> list[str]:
        """Trata as colunas da tabela

        Args:
            colunas (list): _description_

        Returns:
            list[str]: _description_
        """
        coluna_tratadas = []
        for i in colunas:
            i = unidecode(str(i).upper().strip().replace(' ','_').replace("'",""))
            coluna_tratadas.append(i)
        return coluna_tratadas

    @staticmethod
    def criar_data_frame(base: list,colunas: list) -> pd.DataFrame:
        """Cria um Pandas DataFrame

        Args:
            base (list): _description_
            colunas (list): _description_

        Returns:
            pd.DataFrame: _description_
        """
        colunas = Excel.tratar_colunas(colunas)
        df = pd.DataFrame(base,columns=colunas)
        logger.debug('DataFrame created')
        return df

    def exportar_excel(self,excel: dict,index: bool=False) -> None:
        """Exporta para um arquivo excel xlsx

        Args:
            data_frame (pd.DataFrame): _description_
            output (str): _description_
            index (bool, optional): _description_. Defaults to False.
        """
        
        for key in excel.keys():
            excel[key].to_excel(self.writer,sheet_name=key,index=index,engine='xlsxwriter')
        self.writer.close()
        logger.debug(f'{self.file_name} Gerado com sucesso!')

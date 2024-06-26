import re
import socket
import pandas as pd
from unidecode import unidecode
from bs4 import BeautifulSoup
import datetime
from functools import wraps
from time import sleep
import shutil
import os
import random
import string

from .customlogger import logger
from .customexceptions import StopError


remove_espaco = re.compile(r"\s+")
remove_zeros = re.compile(r"[^1-9]")
somente_numeros = re.compile(r'\D')
remove_especiais = re.compile(r"[^a-zA-Z0-9.]+")


def remove_quebra_linha(x):
    return ' '.join(x.strip().split())

def random_generator(size: int=10, chars=string.ascii_lowercase + string.digits) -> str:
        """Gera uma sequencia randomica

        Args:
            size (int, optional): tamanho da string. Defaults to 10.
            chars (_type_, optional): caracteres aceitos na randomizacao. Defaults to string.ascii_lowercase+string.digits.

        Returns:
            str: sequencia randomica
        """
        return ''.join(random.choice(chars) for _ in range(size))

def format_varchar(v):
    valor = str(v).replace("'",'"')
    return f"'{valor}'"

def format_error(message):
    message = ' '.join(str(message).split()).replace("'",'"')
    return message

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def format_dataset(df: pd.DataFrame, varchars: list=[],_datetimes: list=[]):
    
    df.fillna('NULL',inplace=True)
    
    for var in varchars:
        df[var] = df[var].str.replace("'","",regex=False).apply(lambda x: f"'{x}'" if x != 'NULL' or not x else 'NULL')

    for date in _datetimes:
        df[date] = df[date].apply(lambda x: f"'{x.strftime('%Y-%m-%d %H:%M:%S')}'" if x != 'NULL' or not x or type(x) != str else 'NULL')
        
    
    return df

def particionar_lista(base: list,particao: int=1000):
    comandos_update = []
    for i in range(0,len(base),particao):
        linha = base[i:i+particao]
        comandos_update.append(' \n '.join(linha))
    return comandos_update

def formatar_coluna(coluna: str):
    return re.sub(r'[.()]','','_'.join(unidecode(coluna).split()).upper())


def formatar_tabela_html(tabela,nome_tabela: str,width: int,color: str='#465EFF',total=True) -> str:
    """Formata uma tabela html

    Args:
        tabela (_type_): _description_
        nome_tabela (str): _description_
        width (int): _description_

    Returns:
        str: _description_
    """
    soup = BeautifulSoup(tabela,'html.parser')
    new_caption = soup.new_tag("caption",
                                attrs={'style':'''
                                        text-align: center;
                                        font-size: larger;
                                        font-weight: bolder;
                                        font-family: 'Open Sans', sans-serif;
                                                '''})
    new_caption.string = nome_tabela
    soup.find('tbody').attrs['style'] = 'text-align: center;'
    soup.table.attrs['style'] = '''
        background: #012B39;
        border: 2px solid black;
        border-radius: 5px;
        font-family: 'Open Sans', sans-serif;
        text-align: center;
        '''
    soup.table.attrs['width'] = f"{width}%"
    soup.find('table').append(new_caption)
    
    try:
        for th in soup.find('thead').find_all('tr')[1].find_all('th'):
            th.attrs['style'] = '''
                border-bottom: 1px solid #364043;
                color: #E2B842;
                font-weight: bolder;
                padding: 0.65em 1em;
                text-align: center;
            '''
    except: pass
    
    soup.find('thead').find('tr').attrs['style'] = f'''
        text-align: center;
        background-color: {color};
        color: #fff;
        font-size: 16px;
        font-weight: bolder;
        padding: 1em 1em;
        '''
        
    for tr in soup.find('tbody').find_all('tr'):
        for td in tr.find_all('td'):
            td.attrs['style']='''
                color: #fff;
                font-weight: 400;
                padding: 0.65em 1em;
            '''
        tr.find_all('td')[-1].attrs['style']='''
            color: #fff;
            padding: 0.65em 1em;
            font-weight: bolder;
        '''
    
    for tr in soup.find('tbody').find_all('tr'):
        tr.find('td').attrs['style'] = '''
            color: #fff;
            font-weight: 400;
            padding: 0.65em 1em;
            text-align: left;
            '''
    
    if total:
        soup.find_all('tr')[-1].attrs['style'] = '''
                color: #fff;
                padding: 0.65em 1em;
                font-weight: bolder;
            '''

    return soup.prettify()

def saudacao() -> str:
    """Gera a saudacao do email

    Returns:
        str: _description_
    """
    hora_atual = datetime.datetime.now().time().hour
    if hora_atual < 12:
        return 'Bom dia'
    elif hora_atual < 18:
        return 'Boa tarde'
    else:
        return 'Boa noite'

def retry_on_failure(max_retries=5, sleep_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    logger.debug(f'< {retry_on_failure.__name__}: {func.__module__}.{func.__name__} > args: retries: {i}/{max_retries}, sleep_seconds: {sleep_seconds}')
                    return func(*args, **kwargs)
                except StopError as e:
                    raise e
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    _erro = e
                    print(_erro)
                    logger.debug(f'{e.__class__.__name__} | Tentando novamente em: {sleep_seconds} segundos...')
                    sleep(sleep_seconds)
                else:
                    break
            else:
                raise _erro
        return wrapper
    return decorator

def remove_values_from_list(the_list, val):
    return [value for value in the_list if value != val]

def clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    else: raise Exception('Could not clear folder, path does not exist!')

def gerar_tabela_dinamica(
        df: pd.DataFrame,
        index: list[str],
        columns: list[str],
        aggfunc: dict={'ID':pd.Series.nunique}
        ):
        """_summary_

        Args:
            base (pd.DataFrame): _description_
            index (list[str]): _description_
            columns (list[str]): _description_
            aggfunc (dict): _description_

        Returns:
            _type_: _description_
        """        
        df = df.pivot_table(df,index=index,columns=columns,aggfunc=aggfunc,fill_value=0)
        total_coluna = []
        for i in range(len(df)):
            total_i = df.iloc[[i]].sum(axis=1).values
            total_coluna.append(total_i[0])
        df = df.assign(TOTAL = total_coluna)
        total_linha = []
        for i in df.columns:
            total_linha_i = sum(df[i])
            total_linha.append(total_linha_i)
        df.loc['TOTAL'] = total_linha
        try:df = df.rename(columns={'ID':''})
        except: pass
        
        df.reset_index(inplace=True)
        df.columns.set_names([None,None],inplace=True)
        
        return df
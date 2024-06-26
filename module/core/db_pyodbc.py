'''

O código apresentado define uma classe chamada "Database" que é usada para 
conectar-se a um banco de dados usando o módulo "pyodbc". Aqui está uma 
descrição das principais partes do código:

A classe "Database" tem os seguintes atributos estáticos:

"avaliable_drivers": uma lista de strings que contém os nomes dos drivers ODBC 
disponíveis para conexão ao banco de dados.
"CONNECTED": um booleano que indica se a conexão com o banco de dados foi 
estabelecida.
"MAX_ATTEMPTS": um inteiro que define o número máximo de tentativas de conexão 
com o banco de dados.
"TIME_OUT": um inteiro que define o tempo limite em segundos para cada 
tentativa de conexão.

O método __init__ é o construtor da classe. Ele recebe dois argumentos 
opcionais: create_table (booleano) e login (dicionário). O argumento 
create_table indica se as tabelas do sistema devem ser verificadas e criadas 
no banco de dados, se necessário. O argumento login contém as informações de 
conexão, como servidor, banco de dados, usuário e senha.

O método __checkDB__ é usado para verificar se as tabelas do sistema existem 
no banco de dados e criá-las, se necessário. Ele usa consultas SQL para 
verificar a existência das tabelas e, se uma tabela estiver ausente, ela é 
criada usando comandos SQL.

O método __exit__ é usado para encerrar a conexão com o banco de dados. Ele é 
chamado quando o bloco with é concluído ou quando ocorre uma exceção. O método 
fecha o cursor e a conexão com o banco de dados e exibe uma mensagem de log.

O método _commit é usado para fazer o commit das alterações no banco de dados. 
Ele é chamado após a execução de comandos SQL que modificam os dados.

O método rollback é usado para fazer um rollback das alterações no banco de 
dados. Ele é chamado quando ocorre uma exceção durante a execução de comandos 
SQL.

O método execute é usado para executar comandos SQL no banco de dados. Ele 
recebe uma string contendo o comando SQL e retorna uma tupla contendo as 
mensagens do cursor e o número de linhas afetadas.

O método fetchall é usado para recuperar os resultados de uma consulta SQL. 
Ele retorna uma tupla contendo os dados selecionados.

O método select é usado para executar uma consulta SQL e retornar os resultados 
como uma lista de listas. Cada lista interna representa uma linha da tabela.

O método insert é usado para inserir comandos SQL no banco de dados. Ele 
executa o comando SQL e faz o commit das alterações.

O método _get_columns é usado para obter o nome das colunas retornadas por uma 
consulta.

O método select_to_dataframe executa uma consulta SQL no banco de dados e 
retorna o resultado como um objeto DataFrame do pandas.

Os métodos insert_log_robo, gerar_comandos_insert, select_id_mineracao, 
insert_status_robo, update_status_robo_minerando, update_status_robo_concluido, 
update_status_robo_pendente, update_status_robo_error são responsáveis por 
executar operações específicas relacionadas ao banco de dados.

'''
import pyodbc
from platform import system
from time import sleep
import pandas as pd
import numpy as np

from .customlogger import logger

from module.settings import CONEXAO_PADRAO


type_mapping = {
        np.dtype('int64'): 'INT',
        np.dtype('float64'): 'FLOAT',
        np.dtype('bool'): 'BIT',
        np.dtype('datetime64[ns]'): 'DATETIME',
        np.dtype('timedelta64[ns]'): 'TIME',
        np.dtype('object'): 'VARCHAR(MAX)',
        np.dtype('string_'): 'VARCHAR(MAX)'
    }

class Database:
    '''Classe para conectar com o banco de dados usando pyodbc'''

    avaliable_drivers: list[str] = [
        'ODBC Driver 11 for SQL Server',
        'SQL Server Native Client 11.0',
        'ODBC Driver 17 for SQL Server'
    ]

    CONNECTED = False
    MAX_ATTEMPTS: int = 5
    TIME_OUT: int = 120

    def __init__(self,login: dict=CONEXAO_PADRAO) -> None:
        """_summary_

        Args:
            login (dict, optional): _description_. Defaults to Connections.CONNECTIONS['MIS'].
        """
        self._login = login
        
        for i in pyodbc.drivers():
            if i in self.avaliable_drivers:
                self.SQL_DRIVER = i
                logger.info(f'PYODBC DRIVER ::: {i}')
                break
        else:
            logger.critical(f'No SQL driver, please install one of {self.avaliable_drivers} before running this!')
            if str(system()) == 'Linux':
                logger.critical('Linux: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#17')
            elif str(system()) == 'Windows':
                logger.critical('Windows: https://www.microsoft.com/pt-BR/download/details.aspx?id=36434')
            exit()

    def __enter__(self) -> None:
        """Faz MAX_ATTEMPTS tentativas de conexão com o banco de dados\n
        MAX_ATTEMPTS = MAX_ATTEMPTS
        """
        ATTEMPT = 0
        while not self.CONNECTED:
            try:
                self.cnxn = pyodbc.connect(
                    'DRIVER='+self.SQL_DRIVER+';'
                    +'SERVER='+self._login['SERVER']+';'
                    +'DATABASE='+self._login['DATABASE']+';'
                    +'UID='+self._login['USER']+';'
                    +'PWD='+self._login['PASSWORD']
                    ,timeout=1
                    )
                self.cursor = self.cnxn.cursor()
                self.CONNECTED = True
                logger.debug(self._login['NAME']+' CONNECTED')
            except Exception as e:
                self.CONNECTED = False
            ATTEMPT+=1
            if ATTEMPT >= self.MAX_ATTEMPTS:
                logger.warning(f'CONNECTION ERROR ::: MAX ATTEMPTS ::: {ATTEMPT} ::: WAITING {int(self.TIME_OUT/60)} MINUTES ::: {e}')
                ATTEMPT = 0
                sleep(self.TIME_OUT)

    def __exit__(self, *args) -> None:
        """Encerra a conexão com o banco de dados e exibe a mensagem
        """
        if self.CONNECTED:
            try:
                self.cursor.close()
                self.cnxn.close()
                self.CONNECTED = False
                args = list(" ".join(arg.split()) for arg in args)
                logger.debug(f'{args} ::: '+self._login['NAME']+' CONNECTION CLOSED')
            except Exception as e:
                logger.warning(f'Erro ao encerrar conexão com o banco de dados ::: {e}',exc_info=True)
                self.CONNECTED = False

    def commit(self) -> None:
        """Faz o commit no banco de dados
        """
        self.__enter__()
        self.cnxn.commit()
        logger.debug('COMMIT')

    def rollback(self) -> None:
        """Faz o rollback no banco de dados
        """
        self.__enter__()
        self.cnxn.rollback()
        logger.debug('ROWBACK')

    def execute(self,query: str) -> tuple:
        """Executa comandos SQL

        Args:
            query (str): _description_

        Returns:
            tuple: _description_
        """
        self.__enter__()
        self.cursor.execute(query)
        return self.cursor.messages,self.cursor.rowcount

    def executemany(self,query: str,values: list,fast_executemany=True) -> tuple:
        """Executa comandos SQL

        Args:
            query (str): _description_

        Returns:
            tuple: _description_
        """
        self.__enter__()
        if fast_executemany: self.cursor.fast_executemany = True
        self.cursor.executemany(query,values)
        return self.cursor.messages,self.cursor.rowcount
    
    def execute_values(self,query: str, values: list) -> tuple:
        """Executa comandos SQL

        Args:
            query (str): _description_

        Returns:
            tuple: _description_
        """
        self.__enter__()
        self.cursor.execute(query,values)
        return self.cursor.messages,self.cursor.rowcount

    def fetchall(self) -> tuple:
        """Seleciona os dados da pesquisa

        Returns:
            tuple: _description_
        """
        self.__enter__()
        dados = self.cursor.fetchall()
        return dados

    def select(self,query: str,exit=True) -> list[list]:
        """Retorna uma lista de listas com o resultado da QUERY

        Args:
            query (str): _description_

        Returns:
            list[list]: _description_
        """
        self.__enter__()
        message,rowcount = self.execute(query)
        result = self.fetchall()
        result = list(list(i) for i in result)
        if exit: self.__exit__(f'{query}',f'{message}',f'{rowcount}')
        return result

    def insert(self,query: str, exit=True,commit=True) -> tuple:
        """Insere comandos SQL no banco de dados

        Args:
            query (str): _description_

        Returns:
            tuple: _description_
        """
        self.__enter__()
        message,rowcount = self.execute(query)
        if commit: self.commit()
        if exit: self.__exit__(f'{query}',f'{message}',f'{rowcount}')
        return message,rowcount
    
    def insert_values(self,query: str, values: list,exit=True,commit=True) -> tuple:
        """Insere comandos SQL no banco de dados

        Args:
            query (str): _description_

        Returns:
            tuple: _description_
        """
        self.__enter__()
        message,rowcount = self.execute_values(query,values)
        if commit: self.commit()
        if exit: self.__exit__(f'{query}',f'{message}',f'{rowcount}')
        return message,rowcount
    
    def insertmany(self,query: str,values: list, exit=True,commit=True) -> tuple:
        """Insere comandos SQL no banco de dados

        Args:
            query (str): _description_

        Returns:
            tuple: _description_
        """
        self.__enter__()
        message,rowcount = self.executemany(query,values)
        if commit: self.commit()
        if exit: self.__exit__(f'{query}',f'{message}',f'{rowcount}')
        return message,rowcount
    
    def insert_data_frame(self,df: pd.DataFrame, table_name: str,
                          exit=True,commit=True,create_table=False,
                          all_varchar=True,fast_executemany=True) -> tuple:
        """Insere comandos SQL no banco de dados

        Args:
            query (str): _description_
            table_name (str): inserir o nome da tabela no formato "MIS.RPA.JOAOTESTE"

        Returns:
            tuple: _description_
            
        >>> db = Database()
        
        >>> db.insert_data_frame(df,'MIS.RPA.JOAOTESTE',create_table=True)
        
        """
        colunas = []
        
        for column_name, dtype in df.dtypes.items():
            sql_type = type_mapping.get(dtype)
            texto = f'{column_name} {sql_type}'
            colunas.append(texto)
        
        df.fillna('NULL',inplace=True)
        
        if not all_varchar: fast_executemany = False
        
        if fast_executemany: 
            df = df.astype(str)
            all_varchar = True
        
        self.__enter__()
        if create_table:
            
            for i in df.columns.to_list():
                if i.lower() == 'id':
                    coluna_id = i
                    df.rename(columns={coluna_id:'_id'},inplace=True)
                    break
            
            if all_varchar:
                colunas = []
                for column_name in df.columns.to_list():
                    colunas.append(f'[{column_name}] VARCHAR(MAX)')
            
            comando_sql = 'USE '+self._login['DATABASE']+f'''
            IF NOT EXISTS (
            SELECT DISTINCT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name.split('.')[-1]}'
            )
                CREATE TABLE {table_name} (
                ID INT IDENTITY(1,1),
                {','.join(colunas)}
                    )
            '''
            self.insert(comando_sql)
            logger.debug(' '.join(comando_sql.split()))
        
        values = self._tratar_null(df)
        query = self.gerar_insert_statement(df,table_name)
        message,rowcount = self.executemany(query,values,fast_executemany)
        if commit: self.commit()
        if exit: self.__exit__(f'{query}',f'{message}',f'{rowcount}')
        return message,rowcount

    def _tratar_null(self,df):
        '''
        >>> df.fillna('NULL',inplace=True)
        
        >>> lista = df.tratar_null(df)
        
        >>> query = self.gerar_insert_statement(df,table_name)
        
        >>> self.executemany(query,values)
        
        '''
        values = []
        for linha in df.values.tolist():
            _linha = []
            for dado in linha:
                if dado == 'NULL':
                    dado = None
                _linha.append(dado)
            values.append(_linha)
        return values
    
    def create_table(self,table_name,**kwargs):
        '''
        
        >>> db = Database()
        >>> db.create_table('mis.rpa.joaoteste2',
                ID='INT IDENTITY(1,1)',
                NOME='VARCHAR(MAX)',
                IDADE='INT',
                DATA='DATETIME'
                
                )
        '''
        
        colunas = list(f'{key} {value}' for key, value in kwargs.items())
        query = f'''
        CREATE TABLE {table_name} (
        
        {', '.join(colunas)}

        )
        
        '''
        self.insert(query)

    def _get_columns(self) -> list[str]:
        """Seleciona as colunas da consulta

        Returns:
            list[str]: _description_
        """
        columns = list(i[0] for i in self.cursor.description)
        return columns

    def gerar_insert_statement(self,df: pd.DataFrame, table_name: str):
        return f'INSERT INTO {table_name} ({",".join(list(f"[{i}]" for i in df.columns.tolist()))}) VALUES ({",".join(list("?" for i in range(len(df.columns.tolist()))))})'
    
    def select_to_dataframe(self,query: str,fillna=True,exit=True) -> pd.DataFrame:
        """Gera um DataFrame de uma consulta SQL

        Args:
            query (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        self.__enter__()
        message,rowcount = self.execute(query)
        result = self.fetchall()
        colunas = self._get_columns()
        dados = list(list(j for j in i) for i in result)
        df = pd.DataFrame(dados,columns=colunas)
        if fillna: df.fillna('NULL',inplace=True)
        if exit: self.__exit__(f'{query}',f'{message}',f'{rowcount}')
        return df

    def insert_values(self, query: str,values: list, exit=True, commit=True):
        if not self.CONNECTED:
            self.__enter__()
        message,rowcount = self.execute_values(query,values)
        if commit: self.commit()
        if exit: self.__exit__(query)
        return rowcount
    
    def update(self,chave,table_name,chave_column='ID', **kwargs):
        update_string = []
        valores = []
        for key,value in kwargs.items():
            update_string.append(key+' = '+'?')
            valores.append(value)
        update_string = ', '.join(update_string)
        query = f'UPDATE {table_name} SET {update_string} WHERE {chave_column} = ?'
        return self.insert_values(query,valores+[chave])
    
    def gerar_comandos_insert(self,df: pd.DataFrame, tabela: str) -> list:
        """Metodo para gerar comandos insert

        Args:
            base (list): _description_
            colunas (str): _description_
            tabela (str): _description_

        Returns:
            list: _description_
        """
        base = df.astype(str).values.tolist()
        colunas = ','.join(df.columns.tolist())
        lista_comandos_insert = []
        for linha in range(0,len(base),1000):
            lista_valores_formatados = []
            for valores in base[linha:(linha+1000)]:
                unir_valores = ','.join(list(f"[{i}]" for i in valores))
                valores_formatados = f'({unir_valores})'
                lista_valores_formatados.append(valores_formatados)
            comando_insert_linhas =f'''INSERT INTO {tabela} ({colunas}) VALUES {','.join(lista_valores_formatados)}'''
            lista_comandos_insert.append(comando_insert_linhas)
        
        sublists = []
        for i in range(0,len(lista_comandos_insert),100):
            sublist = lista_comandos_insert[i:i+100]
            sublists.append(sublist)
        
        comandos_insert = list('\n'.join(comando) for comando in sublists)
        
        return comandos_insert
    

if __name__ == '__main__':
    db = Database()
    
    
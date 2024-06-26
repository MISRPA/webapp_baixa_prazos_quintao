import pandas as pd
from datetime import datetime
from typing import Literal

from module.core.utils import retry_on_failure, format_error
from module.manager import engine_espelho
from module.models import text
from module import __codname__
from module import settings


PORTAL = 'MIS'

def update_status_TbStatusRobo(status=Literal['running', 'paused'], robo=__codname__):
    with engine_espelho.begin() as con:
        transact = con.execute(text(f'''
            update mis.rpa.TbStatusRobo
            set status = '{status}'
            where robo = '{robo}'
        '''))
    return transact

def update_importacao_TbStatusRobo(status=Literal['running', 'paused'], robo=__codname__):
    with engine_espelho.begin() as con:
        transact = con.execute(text(f'''
            update mis.rpa.TbStatusRobo
            set 
                importacao = :importacao
                ,data = :data
                
            where robo = :robo
        '''), [{
            'importacao': status,
            'robo': robo,
            'data': datetime.now(),
        }])
    return transact

def select_TbStatusRobo(robo=__codname__):
    query = f'''
            select top 1
                *
            from mis.rpa.TbStatusRobo (nolock)
            where robo = '{robo}'
            '''
    with engine_espelho.begin() as con:
        df = pd.read_sql(text(query),con)
        
        if not df.empty:
            return df

        else:
            status = 'paused'
            pd.DataFrame([{
                'robo': robo,
                'status': status,
                'data': datetime.now(),
                'importacao': status,
                'portal': PORTAL
            }]).to_sql(
                name='TbStatusRobo',
                con=engine_espelho,
                schema='rpa',
                if_exists='append',
                index=False
            )
            df = pd.read_sql(text(query),con)
    return df

def select_robo_top_running():
    with engine_espelho.begin() as con:
        df = pd.read_sql(text(f'''
            SELECT TOP 1 * FROM mis.rpa.TbStatusRobo (nolock)
            where status = 'running'
            and portal = '{PORTAL}'
            '''), con)
    return df

def update_erros_legado(table, lista_status=['M', 'E'], status='P'):
    with engine_espelho.begin() as conn:
        transact = conn.execute(text(f'''
            UPDATE {table}
            SET
                STATUS_ROBO = '{status}'
            WHERE STATUS_ROBO IN ({','.join(list(f"'{i}'" for i in lista_status))})
        '''))
    return transact

@retry_on_failure(max_retries=20)
def select_pendente_fila(table):
    with engine_espelho.begin() as conn:
        return pd.read_sql(text(f'''
            SELECT TOP 1
                R.*
            FROM {table} AS R
            WHERE R.STATUS_ROBO = 'P' 
            ORDER BY NEWID()
                        '''), conn)

@retry_on_failure(max_retries=20)
def select_fila_by_status(table, lista_status=['P','M','E','C']):
    with engine_espelho.begin() as conn:
        return pd.read_sql(text(f'''
            SELECT TOP 1
                R.*
            FROM {table} AS R
            WHERE R.STATUS_ROBO IN ({','.join(list(f"'{i}'" for i in lista_status))})
            ORDER BY NEWID()
                        '''), conn)

@retry_on_failure(max_retries=20)
def update_minerando(table, _id):
    with engine_espelho.begin() as conn:
        transact = conn.execute(text(f'''
            UPDATE {table}
            SET
            STATUS_ROBO = 'M'
            ,DATA_ROBO = :DATA_ROBO
            ,LOG_ROBO = :LOG_ROBO
            
            ,PID = :PID
            ,IP = :IP
            ,HOST_NAME = :HOST_NAME
            
            WHERE ID = {_id} AND STATUS_ROBO = 'P'
        '''),[{
        'DATA_ROBO': datetime.now(),
        'LOG_ROBO': 'Realizando rotina',
        
        'PID': settings.PID,
        'IP': settings.IP_ADRESS,
        'HOST_NAME': settings.HOST_NAME,
        }])
    return transact

@retry_on_failure(max_retries=20)
def update_erro(table, _id, e):
    with engine_espelho.begin() as conn:
        transact = conn.execute(text(f'''
            UPDATE {table}
            SET
            STATUS_ROBO = 'E'
            ,DATA_ROBO = :DATA_ROBO
            ,LOG_ROBO = :LOG_ROBO
            
            ,PID = :PID
            ,IP = :IP
            ,HOST_NAME = :HOST_NAME
            
            WHERE ID = {_id} AND STATUS_ROBO != 'C'
        '''),[{
        'DATA_ROBO': datetime.now(),
        'LOG_ROBO': format_error(e),
        
        'PID': settings.PID,
        'IP': settings.IP_ADRESS,
        'HOST_NAME': settings.HOST_NAME,
        }])
    return transact

@retry_on_failure(max_retries=20)
def update_concluido(table, _id):
    with engine_espelho.begin() as conn:
        transact = conn.execute(text(f'''
            UPDATE {table}
            SET
            STATUS_ROBO = 'C'
            ,DATA_ROBO = :DATA_ROBO
            ,LOG_ROBO = :LOG_ROBO
            
            ,PID = :PID
            ,IP = :IP
            ,HOST_NAME = :HOST_NAME
            
            WHERE ID = {_id}
        '''),[{
        'DATA_ROBO': datetime.now(),
        'LOG_ROBO': 'Rotina concluida com sucesso',
        
        'PID': settings.PID,
        'IP': settings.IP_ADRESS,
        'HOST_NAME': settings.HOST_NAME,
        }])
    return transact

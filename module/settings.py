import logging
from platform import system
from dotenv import load_dotenv, find_dotenv
import json
import os
import pyodbc

from module.directory import WORK_DIR


load_dotenv()

ENV_LOC = find_dotenv()

# //////////////////////////////////////////// 
# Carregando configuracoes do .env Obrigatórias:
# //////////////////////////////////////////// 

# Carregando o dicionário serializado do .env
CONEXAO_PADRAO = os.getenv("CONEXAO_PADRAO")

if CONEXAO_PADRAO:
    CONEXAO_PADRAO = json.loads(CONEXAO_PADRAO)
else:
    raise Exception('''Configure a conexão de banco de dados <CONEXAO_PADRAO=json> no arquivo .env
                    
                    >>> Exemplo:
                    {"NAME":"MIS","SERVER":"server","DATABASE":"MIS","USER":"usuario","PASSWORD":"senha"}
                    ''')

# Configurações SQL ALCHEMY --- PROTHEUS ---
CONEXAO_PROTHEUS = os.getenv("CONEXAO_PROTHEUS")

if CONEXAO_PROTHEUS:
    CONEXAO_PROTHEUS = json.loads(CONEXAO_PROTHEUS)
else:
    raise Exception('''Configure a conexão do Protheus <CONEXAO_PROTHEUS=json> no arquivo .env
                    
                    >>> Exemplo:
                    {"NAME":"MIS","SERVER":"server","DATABASE":"MIS","USER":"usuario","PASSWORD":"senha"}
                    ''')
    
CONEXAO_PRODUCAO_ESCRITA = os.getenv("CONEXAO_PRODUCAO_ESCRITA")

if CONEXAO_PRODUCAO_ESCRITA:
    CONEXAO_PRODUCAO_ESCRITA = json.loads(CONEXAO_PRODUCAO_ESCRITA)
else:
    raise Exception('''Configure a conexão de banco de dados <CONEXAO_PRODUCAO_ESCRITA=json> no arquivo .env
                    
                    >>> Exemplo:
                    {"NAME":"MIS","SERVER":"server","DATABASE":"MIS","USER":"usuario","PASSWORD":"senha"}
                    ''')

CONEXAO_EMAIL = os.getenv("CONEXAO_EMAIL")

if CONEXAO_EMAIL:
    CONEXAO_EMAIL = json.loads(CONEXAO_EMAIL)
else:
    raise Exception('''Configure a conexão de e-mail <CONEXAO_EMAIL=json> no arquivo .env
                    
                    >>> Exemplo:
                    {"HOST":"host","PORT":port,"USERNAME":"Equipe MIS","EMAIL":"email@email.com","PASSWORD":"senha"}
                    ''')


CONEXAO_RABBIT = os.getenv("CONEXAO_RABBIT")

if CONEXAO_RABBIT:
    CONEXAO_RABBIT = json.loads(CONEXAO_RABBIT)
else:
    raise Exception('''Configure a conexão do RabbitMQ <CONEXAO_RABBIT=json> no arquivo .env
                    
                    >>> Exemplo:
                    {"USER": "usuario","PASSWORD": "senha","HOST": "host","PORT": 5672,"VHOST": "/"}
                    ''')


# //////////////////////////////////////////// 
# DB Config:
# //////////////////////////////////////////// 

AVAILABLE_DRIVERS = [
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 11 for SQL Server',
        'SQL Server Native Client 11.0',
    ]

for DB_DRIVER in pyodbc.drivers():
    if DB_DRIVER in AVAILABLE_DRIVERS:
        break
else: 
    print(f'No SQL driver, please install one of {AVAILABLE_DRIVERS} before running this!')
    if str(system()) == 'Linux':
        print('Linux: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#17')
    elif str(system()) == 'Windows':
        print('Windows: https://www.microsoft.com/pt-BR/download/details.aspx?id=36434')
    raise Exception('Driver not available. Please install the driver first before running this!')

# Configuração do SQLAlchemy base espelho
DB_SERVER = CONEXAO_PADRAO['SERVER']
DATABASE = CONEXAO_PADRAO['DATABASE']
DB_USER = CONEXAO_PADRAO['USER']
DB_PASSWORD = CONEXAO_PADRAO['PASSWORD']

DATABASE_URI = f"mssql+pyodbc:///?odbc_connect=DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DATABASE};UID={DB_USER};PWD={DB_PASSWORD}"

# Configuração do SQLAlchemy protheus
DB_SERVER_PROTHEUS = CONEXAO_PROTHEUS['SERVER']
DATABASE_PROTHEUS = CONEXAO_PROTHEUS['DATABASE']
DB_USER_PROTHEUS = CONEXAO_PROTHEUS['USER']
DB_PASSWORD_PROTHEUS = CONEXAO_PROTHEUS['PASSWORD']

DATABASE_URI_PROTHEUS = f"mssql+pyodbc:///?odbc_connect=DRIVER={DB_DRIVER};SERVER={DB_SERVER_PROTHEUS};DATABASE={DATABASE};UID={DB_USER_PROTHEUS};PWD={DB_PASSWORD_PROTHEUS}"

# Configuração do SQLAlchemy base produção
DB_SERVER_PRODUCAO_ESCRITA = CONEXAO_PRODUCAO_ESCRITA['SERVER']
DATABASE_PRODUCAO_ESCRITA = CONEXAO_PRODUCAO_ESCRITA['DATABASE']
DB_USER_PRODUCAO_ESCRITA = CONEXAO_PRODUCAO_ESCRITA['USER']
DB_PASSWORD_PRODUCAO_ESCRITA = CONEXAO_PRODUCAO_ESCRITA['PASSWORD']

DATABASE_URI_PRODUCAO_ESCRITA = f"mssql+pyodbc:///?odbc_connect=DRIVER={DB_DRIVER};SERVER={DB_SERVER_PRODUCAO_ESCRITA};DATABASE={DATABASE};UID={DB_USER_PRODUCAO_ESCRITA};PWD={DB_PASSWORD_PRODUCAO_ESCRITA}"

# //////////////////////////////////////////// 
# Captcha Config:
# //////////////////////////////////////////// 

BCS_TOKEN = os.getenv("BCS_TOKEN")

# //////////////////////////////////////////// 
# Log Config:
# //////////////////////////////////////////// 

LOG_LEVEL = os.getenv("LOG_LEVEL", 'INFO')

LOG_LEVEL = logging._nameToLevel.get(LOG_LEVEL)

# //////////////////////////////////////////// 
# PID:
# //////////////////////////////////////////// 

PID = os.getpid()

# //////////////////////////////////////////// 
# RUNNER INSTANCES CONFIG:
# //////////////////////////////////////////// 

DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')

RUN_INSTANCES = os.getenv("RUN_INSTANCES", 'False').lower() in ('true', '1', 't')
USE_VENV = os.getenv("USE_VENV", 'False').lower() in ('true', '1', 't')


# //////////////////////////////////////////// 
# BROWSER CONFIG:
# //////////////////////////////////////////// 

TOKEN_NOPECHA = os.getenv("TOKEN_NOPECHA")
HEADLESS = os.getenv("HEADLESS", 'False').lower() in ('true', '1', 't')
INSTALL = os.getenv("INSTALL", 'False').lower() in ('true', '1', 't')
CAPTCHA_MANUAL = os.getenv("CAPTCHA_MANUAL", 'False').lower() in ('true', '1', 't')

RUNNER = 'python'

if system() == 'Windows':
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    if USE_VENV:
        RUNNER = os.path.join('venv','Scripts','python')

elif system() == 'Linux':
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36'
    HEADLESS = True
    CAPTCHA_MANUAL = False
    if USE_VENV:
        RUNNER = os.path.join('venv','bin','python')

if HEADLESS:
    CAPTCHA_MANUAL = False

if DEBUG:
    RUN_INSTANCES = False
    HEADLESS = False
    print('WARNING: Running in debug mode!')


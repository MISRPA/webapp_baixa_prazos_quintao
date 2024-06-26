import streamlit as st
import plotly.express as px
import pandas as pd
import os
import streamlit_authenticator as stauth 
from PIL import Image
import io
import yaml
from yaml.loader import SafeLoader
from datetime import datetime, timedelta
import psutil
from io import StringIO

from module.manager import engine_espelho
from module.models import text
from module import settings
from module.directory import Directory
from module.core.utils import retry_on_failure
from module import __version__
from module.app.pages.auth.auth import select_usuarios
from module.app.pages.auth.users import pagina_gerenciar_usuarios
from module.app.pages.prazos import baixa
from module.core.customlogger import logger



TITLE = "Portal MIS"


@retry_on_failure(5, 30)    
def consulta_clientes():
    with engine_espelho.begin() as con:
        df = pd.read_sql(text(f'''
SELECT C.IdCliente, C.NomeInterno
FROM TOTAL_FC.DBO.tbClientes AS C
WHERE C.Status = 'ATIVO'
ORDER BY C.NOMEINTERNO ASC
        '''), con)
    return df

def mostrar_informacoes_aplicacao():
    pid = settings.PID
    processo = psutil.Process(pid)
    cpu_percent_aplicacao = processo.cpu_percent(interval=1)
    mem_info_aplicacao = processo.memory_info()
    
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_info = psutil.virtual_memory()
    
    limite_memoria = f'{mem_info.total / (1024 * 1024):.2f}'
    uso_mem_app = f'{mem_info_aplicacao.rss / (1024 * 1024):.2f}'
    uso_mem_pc = f'{mem_info.used / (1024 * 1024):.2f}'

    mem_app_percent = f'{float(uso_mem_app) / float(limite_memoria) * 100:.2f}'
    
    medio = 40
    limite = 80
    if mem_info.percent >= limite or cpu_percent >= limite:
        container = st.sidebar.error
    elif mem_info.percent >= medio or cpu_percent >= medio:
        container = st.sidebar.warning
    else:
        container = st.sidebar.info
    
    container(f"""
### Informações do Servidor:

PID da Aplicação: {pid}

Uso de CPU:
- App: {cpu_percent_aplicacao}%
- PC: {cpu_percent}%

Uso de Memória:
- Limite: {limite_memoria} MB
- App: {mem_app_percent}% | {uso_mem_app} MB
- PC: {mem_info.percent}% | {uso_mem_pc} MB
                    """)

def exibir_outros_apps():

    st.sidebar.markdown(
    """
    <style>
        .dropdown {
            position: relative;
            display: inline-block;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
        }
        .dropdown:hover .dropdown-content {
            display: block;
        }
        .dropdown-item {
            padding: 12px 16px !important;
            display: block !important;
            text-decoration: none !important;
            color: #0080ff !important;
        }
        .dropdown-item:hover {
            background-color: #ddd;
        }
    </style>
    """
    , unsafe_allow_html=True
    )

    st.sidebar.markdown("<div class='dropdown'>", unsafe_allow_html=True)
    st.sidebar.markdown("  <span>Outros Apps disponíveis</span>", unsafe_allow_html=True)
    st.sidebar.markdown("  <div class='dropdown-content'>", unsafe_allow_html=True)

    links = {
        'Robô Custas Financeiro': 'http://10.0.211.82:5000/',
        'Robô Consultas CEF': 'http://10.0.211.82:8001/',
        'Api Documentos Terceirização CEF': 'http://10.0.211.82:9050/docs/',
        'Robô Api DataJud': 'http://10.0.211.82:8506/',
        'Robô Pesquisa Andamentos BB': 'http://10.0.211.82:8501/',
        'Robô Operação Liquida BB': 'http://10.0.211.82:8502/',
        'Robô Relatórios': 'http://10.0.211.82:8503/',
        'Robô Financeiro Terceirização BB': 'http://10.0.211.82:8504/',
        'Robô Rastreamento Andamentos BB': 'http://10.0.211.82:8505/',
        'Robô Sentença BB': 'http://10.0.211.82:8508/',
        'Robô Higienização BB': 'http://10.0.211.82:8509/',
    }

    for name, link in links.items():
        st.sidebar.markdown(f"    <a class='dropdown-item' target='_blank' href='{link}'>{name}</a>", unsafe_allow_html=True)

    st.sidebar.markdown("  </div>", unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    
# Página principal

def main():
    
    logo = Image.open(os.path.join(Directory.TEMPLATES.value,'img', 'logo_fc.png'))
    fav_icon = Image.open(os.path.join(Directory.TEMPLATES.value,'img', 'favicon.ico'))

    st.set_page_config(page_title=f'Relatórios - MIS', page_icon=fav_icon,layout='wide')

    st.markdown(""" 
    <style> 

        .font {                                          
            font-size:30px; 
            font-family: 'Cooper Black'; 
            color: white;
            } 

        #MainMenu {
            visibility: hidden;
        }
        
        .css-10pw50.ea3mdgi1 {
            visibility: hidden;
        }
        
        .css-vk3wp9 {
            background-color: #333333 !important;
            color: black !important;
        }
        
        
    </style> """, unsafe_allow_html=True)
    
    st.sidebar.image(logo)
    
    df_users = select_usuarios()
    df_users = df_users[df_users['ATIVO'] == True].copy()
    
    usernames = df_users['USERNAME'].values.tolist()
    emails = df_users['EMAIL'].values.tolist()
    names = df_users['NOME'].values.tolist()
    hashed_pass = df_users['PASSWORD'].values.tolist()
    roles = df_users['ROLE'].values.tolist()
    
    credentials = {}
    for username, name, password, role, email in zip(usernames, names, hashed_pass, roles, emails):
        credentials.setdefault('usernames', {})[username] = {
            'email': email,  # Ajuste conforme necessário
            'name': name,
            'password': password,
            'role': role
        }
    
    authenticator = stauth.Authenticate(
        credentials,
        key='wa_relatorios_mis',
        cookie_name='wa_relatorios_mis',
        cookie_expiry_days=1,
        preauthorized='joao.almeida@ferreiraechagas.com.br'
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    texto_no_user = ":warning: Caso não tenha um acesso, gentileza abrir um chamado à equipe MIS solicitando o acesso."

    if authentication_status == False:
        st.error(":heavy_exclamation_mark: Usuário ou senha incorretos.")
        st.warning(texto_no_user)

    if authentication_status == None:
        st.warning(texto_no_user)
    
    if authentication_status:
        
        st.sidebar.success(f"""
            - Nome: {name}
            - Usuário: {username}
            """)
        
        st.sidebar.info(f"**Versão:** {__version__}")
        
    if authentication_status:
        user_data = credentials['usernames'][username]
        
        authenticator.logout("Logout", "sidebar")

        if user_data['role'] == 'admin':
            opcoes_users = [
                "Usuário não associado",
                
                "Baixa de Prazos",
                
                "Gerenciar Usuários",
                ]
            mostrar_informacoes_aplicacao()
            
        if user_data['role'] == 'user':
            opcoes_users = [
                "Usuário não associado",
            ]
            
        if username in baixa.USUARIOS_PERMITIDOS:
            opcoes_users+=['Baixa de Prazos']

        dropdown_opcoes = st.sidebar.selectbox("Escolha uma opção:", opcoes_users)
        
        # Opções de aplicações:
            
        if dropdown_opcoes == "Gerenciar Usuários":
            pagina_gerenciar_usuarios()
            
        elif dropdown_opcoes == "Baixa de Prazos":
            baixa.pagina_baixa_prazos(user_data)
        
        elif dropdown_opcoes == "Usuário não associado":
            st.warning(':warning: Seu usuário não está associado a nenhum grupo. \n\n Gentileza abrir um chamado para inclusão no grupo necessário.')
    else:
        st.error('Usuário não autenticado!')
        
    exibir_outros_apps()

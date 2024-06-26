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
from module.core.customlogger import logger

from .querys import QUERY_BATIMENTO, DICIO_SELECT_QUERY

# /////////////////////////////////////////////////////////////////////////

def change_pagina_atual(pagina_atual):
    if pagina_atual != st.session_state['pagina_atual']:
        st.session_state['pagina_atual'] = pagina_atual
        st.experimental_rerun()

def download_report():
    with engine_espelho.begin() as con:
        con.execute(text("TRUNCATE TABLE MIS.RPA.BASEBATIMENTOCADASTRAMENTOBB"), con)
    print('tabela truncada')

def batimento_por_processo(name, consulta_clientes, DICIO_SELECT_QUERY, download_report):
    st.header('Batimento de Processos')
            
    with st.expander(':information_source: Informações sobre a aplicação'):
        st.info(f'''
Bem vindo(a), {name}! \n\n 
Esta aplicação facilita a realização do batimento de processos pelos campos de Controle Cliente, Número Processo CNJ ou Pasta. \n\n 
Para que funcione corretamente, é necessário selecionar os clientes a serem consultados e inserir um arquivo excel com uma coluna que **contenha o nome exatamente igual a:
"CONTROLECLIENTE", "NUMPROCESSOCNJ" ou "PASTA"**. \n\n
:warning: :orange[**O conteúdo da coluna a ser realizada a consulta, deverá estar formatada com todos os padrões.**] :warning: \n
Após o upload, você poderá selecionar por qual campo será realizado o batimento e clicar no botão "Realizar Insert e Gerar Relatório". \n\n
:warning: :orange[**Esta operação pode demorar um pouco, de acordo com a quantidade de processos.**] :warning: \n
Neste momento a aplicação fará uma inserção dos dados enviados e uma consulta em nosso banco de dados. \n
Com a consulta realizada, você poderá selecionar quais colunas você deseja que seja incluída em seu relatório final, lembrando que será disponibilizado na ordem selecionada. Mas será disponibilizado um exemplo logo a baixo. \n
Ao completar o processo, basta clicar no botão "Download Relatório" que será realizado o download do arquivo final.
                    ''', 
                    icon="ℹ️"
                )
            
            
    arquivo_excel = 'batimento_mis.xlsx'
    
    df_cliente = consulta_clientes()
    
    select_cliente = st.multiselect(
        label='Selecione os clientes a serem incluídos no relatório:', 
        placeholder='Escolha uma opção',
        options=df_cliente['NomeInterno'], 
        default=None,
        
        )
    
    print(select_cliente)
    
    if not select_cliente:
        st.warning("Gentileza realizar a inclusão de ao menos um cliente.")
        
    else:
        # Processo de upload do arquivo e transformação em DataFrame
        uploaded_file = st.file_uploader("Escolha um arquivo", type=['xlsx'])
        if uploaded_file is not None:
            dataframe = pd.read_excel(uploaded_file)
            colunas = list(e.lower() for e in dataframe.columns.tolist())
            
            with st.container():
                opcao_batimento = st.selectbox(
                    'Selecione por qual campo será feito o batimento:', 
                    list(i for i in DICIO_SELECT_QUERY.keys())
                    )
                dataframe = pd.read_excel(uploaded_file)
                select_colunas = list(e.lower() for e in dataframe.columns.tolist())
                colunas = {e: e.lower() for e in dataframe.columns.tolist()}
                dataframe.rename(columns=colunas, inplace=True)

            if opcao_batimento in select_colunas:  
                col1, col2, *_ = st.columns(3)
                if col1.button('Gerar relatório'):
                    with st.spinner('Realizando Insert'):
                        dataframe[opcao_batimento].to_sql(
                            'BASEBATIMENTOCADASTRAMENTOBB', 
                            schema='RPA',
                            con=engine_espelho, 
                            if_exists='append', 
                            index=False
                            )
                            
                        # Exibição dos comandos SQL gerados
                        st.success('Insert realizado.')
                        logger.info('insert realizado')
                    
                with st.spinner('Carregando informações, aguarde...'):
                    lista_id_clientes = df_cliente[df_cliente['NomeInterno'].isin(select_cliente)]['IdCliente'].astype(str).tolist()
                    consulta_result = pd.read_sql(text(QUERY_BATIMENTO.format(
                        ligacao_select = DICIO_SELECT_QUERY.get(opcao_batimento),
                        lista_id_clientes = ','.join(lista_id_clientes)
                        )), con=engine_espelho
                        )
                    select_coluna = st.multiselect(
                        label='Selecione as colunas a serem incluídas no relatório:', 
                        options=consulta_result.columns.tolist(), 
                        default=['CLIENTE', 'PASTA', 'STATUS', 'NUMPROCESSOCNJ', 'CONTROLECLIENTE', 'NÚCLEO']
                        )
                    print(f"Consulta realizada")
                    logger.info(f"Consulta realizada")
                    
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        consulta_result[select_coluna].fillna('NULL').to_excel(writer, index=False, sheet_name='BASE')
                    
                    st.write('Exemplo do relatório:')
                    st.table(consulta_result[select_coluna].head(1))
                    
                    buffer.seek(0)

                    print(f"Arquivo Excel Gerado. Campos utilizados: {consulta_result[select_coluna].columns.tolist()}")
                    logger.info(f"Arquivo Excel Gerado. Campos utilizados: {consulta_result[select_coluna].columns.tolist()}")
                    st.success(f"Relatório gerado com sucesso!")
                    
                    if col2.download_button(label="Download Relatório", data=buffer.read(), file_name=arquivo_excel, on_click=download_report):
                        pass
            else:
                        st.button('Realizar Insert e gerar relatório', disabled=True)
                        st.error(f"A coluna {opcao_batimento} não foi encontrada no arquivo carregado. Por favor, adicione um arquivo com as informações necessárias.")
                        logger.error(f"A coluna {opcao_batimento} não foi encontrada no arquivo carregado. Por favor, adicione um arquivo com as informações necessárias.")
                